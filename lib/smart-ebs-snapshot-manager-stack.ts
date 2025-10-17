import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as dynamodb from "aws-cdk-lib/aws-dynamodb";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as apigateway from "aws-cdk-lib/aws-apigateway";

export class SmartEbsSnapshotManagerStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // ==========================================================
    // 🗃️ ① DynamoDB 테이블 생성
    // ==========================================================
    const snapshotsTable = new dynamodb.Table(this, "SnapshotsTable", {
      partitionKey: { name: "snapshotId", type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    const policiesTable = new dynamodb.Table(this, "PoliciesTable", {
      partitionKey: { name: "policy_id", type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // ==========================================================
    // ⚙️ ② 공통 Lambda 설정
    // ==========================================================
    const commonLambdaProps = {
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset("lambda"),
      environment: {
        SNAPSHOT_TABLE: snapshotsTable.tableName,
        POLICY_TABLE: policiesTable.tableName,
      },
      timeout: cdk.Duration.seconds(30),
      memorySize: 256,
    };

    // ==========================================================
    // 🧩 ③ Lambda 함수 정의
    // ==========================================================

    // ✅ 스냅샷 목록 조회
    const listSnapshotsFn = new lambda.Function(this, "ListSnapshotsFn", {
      ...commonLambdaProps,
      handler: "api.list_snapshots.handler",
    });

    // ✅ 정책 목록 조회
    const listPoliciesFn = new lambda.Function(this, "ListPoliciesFn", {
      ...commonLambdaProps,
      handler: "api.list_policies.handler",
    });

    // ✅ 스냅샷 생성
    const createSnapshotFn = new lambda.Function(this, "CreateSnapshotFn", {
      ...commonLambdaProps,
      handler: "api.create_snapshot.lambda_handler",
    });

    // ✅ 스냅샷 삭제
    const deleteSnapshotFn = new lambda.Function(this, "DeleteSnapshotFn", {
      ...commonLambdaProps,
      handler: "api.delete_snapshot.handler",
    });

    // ✅ 정책 생성
    const createPolicyFn = new lambda.Function(this, "CreatePolicyFn", {
      ...commonLambdaProps,
      handler: "api.create_policy.handler",
    });

    // ✅ 정책 수정
    const updatePolicyFn = new lambda.Function(this, "UpdatePolicyFn", {
      ...commonLambdaProps,
      handler: "api.update_policy.handler",
    });

    // ==========================================================
    // 🔐 ④ DynamoDB 접근 권한 부여
    // ==========================================================
    snapshotsTable.grantReadWriteData(listSnapshotsFn);
    snapshotsTable.grantReadWriteData(createSnapshotFn);
    snapshotsTable.grantReadWriteData(deleteSnapshotFn);

    policiesTable.grantReadWriteData(listPoliciesFn);
    policiesTable.grantReadWriteData(createPolicyFn);
    policiesTable.grantReadWriteData(updatePolicyFn);

    // ==========================================================
    // 🌐 ⑤ API Gateway 설정
    // ==========================================================
    const api = new apigateway.RestApi(this, "SmartEbsApi", {
      restApiName: "SmartEBS Snapshot Manager API",
      description: "Manage EBS snapshots and backup policies",
    });

    // ====== /list 경로 ======
    const list = api.root.addResource("list");
    list.addResource("snapshots").addMethod("GET", new apigateway.LambdaIntegration(listSnapshotsFn));
    list.addResource("policies").addMethod("GET", new apigateway.LambdaIntegration(listPoliciesFn));

    // ====== /create 경로 ======
    const create = api.root.addResource("create");
    create.addResource("snapshot").addMethod("POST", new apigateway.LambdaIntegration(createSnapshotFn));
    create.addResource("policy").addMethod("POST", new apigateway.LambdaIntegration(createPolicyFn));

    // ====== /delete 경로 ======
    const del = api.root.addResource("delete");
    del.addResource("snapshot").addMethod("POST", new apigateway.LambdaIntegration(deleteSnapshotFn));

    // ====== /update 경로 ======
    const update = api.root.addResource("update");
    update.addResource("policy").addMethod("POST", new apigateway.LambdaIntegration(updatePolicyFn));

    // ==========================================================
    // 📤 ⑥ 출력 (API URL)
    // ==========================================================
    new cdk.CfnOutput(this, "ApiEndpoint", {
      value: api.url ?? "Something went wrong",
    });
  }
}

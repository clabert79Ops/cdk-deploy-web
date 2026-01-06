from aws_cdk import (
    Stack,
    aws_cloudfront,
    aws_cloudfront_origins,
    aws_s3,
    aws_s3_deployment,
    Duration,
    CfnOutput
)

from constructs import Construct
import os
class PyWebdeplStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        deployment_bucket = aws_s3.Bucket(self, 
                                          "PyWebDeplBucket")
        
        ui_dir = os.path.join(os.path.dirname(__file__), "..", '..', 'web', 'dist')
        if not os.path.exists(ui_dir):
            print("UI not found --->>> " + ui_dir)
            raise FileNotFoundError(f"UI not found at {ui_dir}")
        
        origin_identity = aws_cloudfront.OriginAccessIdentity(self, 
                                                              "PyWebDeplOriginAccessIdentity"
                                                            
                                                            )
        
        deployment_bucket.grant_read(origin_identity)
        
        distribution = aws_cloudfront.Distribution(
                self,
                "PyWebDeploymentDistribution",
                default_root_object="index.html",
                default_behavior=aws_cloudfront.BehaviorOptions(
                    origin=aws_cloudfront_origins.S3Origin(
                    deployment_bucket,
                    origin_access_identity=origin_identity
                )
        ),
        
        error_responses=[
            aws_cloudfront.ErrorResponse(
                http_status=403,
                response_http_status=200,
                response_page_path="/index.html",
                ttl=Duration.seconds(0),
        ),
        aws_cloudfront.ErrorResponse(
            http_status=404,
            response_http_status=200,
            response_page_path="/index.html",
            ttl=Duration.seconds(0),
        ),
    ],
)
        
        aws_s3_deployment.BucketDeployment(
            self,"PyWebDeployment",
            sources=[aws_s3_deployment.Source.asset(ui_dir)],
            destination_bucket=deployment_bucket,
            distribution=distribution,
            )

        CfnOutput(self, "PyAppUrl", 
                  value=distribution.distribution_domain_name)
        
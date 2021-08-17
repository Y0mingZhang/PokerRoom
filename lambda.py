import json


"""
Types of requests:

start {startgame} 




"""
def lambda_handler(event, context):
    
    query = event["queryStringParameters"]
    response = {"text" : "hello 啊啊啊啊", "options" : ['a', 'b', 'c', 'd']}

    return {
        'statusCode': 200,
        'body': json.dumps(response),
    }

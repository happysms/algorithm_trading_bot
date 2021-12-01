from return_rate_record import ReturnRateRecord


def lambda_handler(event, context):
    obj = ReturnRateRecord()
    obj.insert_record_to_database()

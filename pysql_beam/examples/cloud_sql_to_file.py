"""
This read some data from cloud sql mysql database
and write to file

Command to run this script:

python cloud_sql_to_file.py --host localhost --port 3306 --database SECRET_DATABASE \
--username SECRET_USER --password SECRET_PASSWORD --table YOUR_TABLE --output YOUR_OUTPUT_FLLE


For postgres sql:
python cloud_sql_to_file.py  --host localhost  --port 5432 --database SECRET_DATABASE \
--username SECRET_USER --password SECRET_PASSWORD --table YOUR_TABLE --output YOUR_OUTPUT_FLLE

"""
import sys
sys.path.insert(0, '/home/jupyter/shapiro-johannes/pysql-beam/pysql-beam')
sys.path.insert(0, '/home/jupyter/shapiro-johannes/pysql-beam')
import logging
import apache_beam as beam
from pysql_beam.sql_io.sql import SQLSource, SQLWriter, ReadFromSQL
from pysql_beam.sql_io.wrapper import MySQLWrapper, PostgresWrapper
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions


def log(row, level="debug"):
    getattr(logging, level.lower())(row)
    return row


class SQLOptions(PipelineOptions):

    @classmethod
    def _add_argparse_args(cls, parser):
        # parser.add_value_provider_argument('--host', dest='host', required=False)
        # parser.add_value_provider_argument('--port', dest='port', required=False)
        # parser.add_value_provider_argument('--database', dest='database', required=False)
        # parser.add_value_provider_argument('--table', dest='table', required=False)
        # parser.add_value_provider_argument('--query', dest='query', required=False)
        # parser.add_value_provider_argument('--username', dest='username', required=False)
        # parser.add_value_provider_argument('--password', dest='password', required=False)
        # parser.add_value_provider_argument('--output', dest='output', required=False, help="output file name")
        # parser.add_value_provider_argument('--output_table', dest='output_table', required=True, help="output_table name")
        parser.add_value_provider_argument('--host', dest='host', default="localhost")
        parser.add_value_provider_argument('--port', dest='port', default="3306")
        parser.add_value_provider_argument('--database', dest='database', default="dverma")
        parser.add_value_provider_argument('--query', dest='query', default="SELECT * FROM dverma.userPointsLedger;")
        parser.add_value_provider_argument('--username', dest='username', default="dverma")
        parser.add_value_provider_argument('--password', dest='password', default="Deepak@123")
        parser.add_value_provider_argument('--output', dest='output', default="abc", help="output file name")
        parser.add_value_provider_argument('--output_table', dest='output_table', required=False, help="output_table name")


def transform_records(row, new_col='user_id'):
    # iid = row.pop('id') or 1
    # row['user_id'] = iid
    return row


def run():
    pipeline_options = PipelineOptions()
    options = pipeline_options.view_as(SQLOptions)
    options.view_as(SetupOptions).save_main_session = True

    pipeline = beam.Pipeline(options=options)

    mysql_data = pipeline | ReadFromSQL(host=options.host, port=options.port,
                                        username=options.username, password=options.password,
                                        databae=options.database, query=options.query,
                                        wrapper=MSSQLWrapper,
                                        #wrapper=MySQLWrapper,
                                        # wrapper=PostgresWrapper
                                        #
                                        )

    transformed_data = mysql_data | "Transform records" >> beam.Map(transform_records, 'user_id')
    # transformed_data | "insert into mysql" >> SQLWriter(options.host, options.port,
    #                                                     options.username, options.password,
    #                                                     options.database,
    #                                                     table='output',
    #                                                     wrapper=MySQLWrapper, autocommit=True, batch_size=500)
    # transformed_data | "insert into postgres" >> SQLWriter(options.host, 5432,
    #                                                        'postgres', options.password,
    #                                                        options.database, table=options.output_table,
    #                                                        wrapper=PostgresWrapper, autocommit=False, batch_size=500)
    mysql_data | "Log records " >> beam.Map(log) | beam.io.WriteToText(options.output, num_shards=1, file_name_suffix=".json")

    pipeline.run().wait_until_finish()


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.WARNING)
    run()

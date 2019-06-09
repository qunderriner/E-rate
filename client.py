import psycopg2 as pg
import connection
import logging

logger= logging.getLogger('erates')

TABLES = ['applications', 'consultants', 'reviews']

#what's original discount? 
BULK_CREATE = [
        """
        CREATE TABLE bulk_temp (
            colid INT
            , application_number    INT
            , orig_funding_request  INT
            , cmtd_funding_request    INT
            , consulting_firms_name   varchar(255)
            , consulting_firms_email  varchar(255)
            , applicant_type  varchar(255)
            , applicant_city  varchar(100)
            , applicant_state varchar(100)
            , cmtd_discount   INT
            , service_type    varchar(100)
            , function    varchar(100)
            , funding_gap INT
            )
        """ 
    ]


CREATE_COMMANDS = [
    """
    CREATE TABLE applications (
        request_id                    SERIAL PRIMARY KEY,
        application_number            INT           ,
        cmtd_funding_request          INT           ,
        consultant                    varchar(100)  ,
        applicant_type                varchar(100)  ,
        applicant_city                varchar(100)  ,
        applicant_state               varchar(100)  ,
        cmtd_discount                 INT           ,
        service_type                  varchar(100)  ,
        function                      varchar(100)  ,
        funding_gap                   INT           
        );
    """,
    """
    CREATE TABLE consultants (
        name                      varchar(100)      ,
        email                     varchar(100)      
        );
    """,
    """
    CREATE TABLE reviews (
        id                        SERIAL PRIMARY KEY,
        consultant_name           varchar(100)      ,
        description               text              ,
        date_added                date              
        -- foreign key (consultant_name) references consultants(name)
        );
    """]

BULK_INSERTS = [
    """
    INSERT INTO applications (
        application_number
        , cmtd_funding_request
        , consultant
        , applicant_type
        , applicant_city
        , applicant_state
        , cmtd_discount
        , service_type
        , function
        , funding_gap)
    SELECT  application_number
        , cmtd_funding_request
        , consulting_firms_name
        , applicant_type
        , applicant_city
        , applicant_state
        , cmtd_discount
        , service_type
        , function
        , funding_gap
    FROM bulk_temp
    ON CONFLICT DO NOTHING;
    """,
    """
    INSERT INTO consultants (
        name
        , email)
    SELECT DISTINCT 
        consulting_firms_name
        , consulting_firms_email
    FROM bulk_temp
    ON CONFLICT DO NOTHING;
    """
    ]



class client:
    def __init__(self):
        self.dbname=connection.dbname
        self.dbhost=connection.dbhost
        self.dbport=connection.dbport
        self.dbusername=connection.dbusername
        self.dbpasswd=connection.dbpasswd

        # added meself
        self.conn=None

    # open a connection to a psql database, using the self.dbXX parameters
    def open_connection(self):
        logger.debug("Opening a Connection")

        #TODO HW
        self.conn = pg.connect(host=self.dbhost, database=self.dbname, user=self.dbusername, password=self.dbpasswd, port=self.dbport)

        return True

    def is_open(self):
        return (self.conn is not None)

    # Close any active connection(should be able to handle closing a closed conn)
    def close_connection(self):
        logger.debug("Closing Connection")
        
        #TODO HW
        if self.is_open():
            self.conn.close()
            self.conn = None

        return True


    # Load the inspection data via TSV loading or via hbase. Use happybase as the library for hbase
    # hbase == hbase
    def load_inspection(self, load_file=None):
        logger.debug("Loading Inspection")
        if load_file == None:
            raise Exception("No Load Details Provided")
        else:
            if not self.is_open():
                self.open_connection()

            cur = self.conn.cursor()
            drop_statement = 'DROP TABLE IF EXISTS bulk_temp;'
            cur.execute(drop_statement)
            cur.execute(BULK_CREATE[0])

            copy_sql = """
            COPY bulk_temp FROM stdin WITH CSV HEADER
            DELIMITER as ','
            """


            with open(load_file, 'r') as f:
                try:
                    cur.copy_expert(sql=copy_sql, file=f)
                    for insert in BULK_INSERTS:
                        cur.execute(insert)
                    
                except (Exception, pg.DatabaseError) as error:
                    print(error)
                finally:
                    if self.conn is not None:
                        self.conn.commit()
                        cur.close()
                        self.close_connection()
        #TODO HW
        return None

    def build_tables(self):
        logger.debug("Building Tables")
        self.open_connection()
        #TODO HW

        if not self.conn:
            self.open_connection

        cur = self.conn.cursor()
        for table in TABLES:
            drop_statement = 'DROP TABLE IF EXISTS {} CASCADE;'.format(table)
            cur.execute(drop_statement)

        for command in CREATE_COMMANDS:
            cur.execute(command)

        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        self.conn.commit()
        self.close_connection()

        return None


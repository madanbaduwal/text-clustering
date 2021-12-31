from dynaconf import Dynaconf

from pathlib import Path
from src.utils.aws import S3,SQS

_BASE_PATH = Path(__file__).parent.parent.parent
_CONFIG_PATH = _BASE_PATH / "configs"


class ProjectConfig(Dynaconf):
    def __init__(self, **options):
        super(ProjectConfig, self).__init__(**options)

        self.ENVIRONMENT = self.ENV_FOR_DYNACONF.lower()
        self.base_path = _BASE_PATH
        self.config_path = _CONFIG_PATH

        
        self.LOCAL_DATA_DIR = self.base_path /'data/final'
        self.LOCAL_MODEL_DIR = self.base_path /'models'
        self.LOCAL_log_path = self.base_path / "logs"

        self.LOCAL_RESOURCE_DIR = str(Path(self.base_path, 'resources'))

        self.LOCAL_DATA_DIR = Path(self.LOCAL_RESOURCE_DIR, self.LOCAL_DATA_DIR)
        if not self.LOCAL_DATA_DIR.exists():
            self.LOCAL_DATA_DIR.mkdir(parents=True)
        self.LOCAL_DATA_DIR = str(self.LOCAL_DATA_DIR)

        self.LOCAL_MODEL_DIR = Path(self.LOCAL_RESOURCE_DIR, self.LOCAL_MODEL_DIR)
        if not self.LOCAL_MODEL_DIR.exists():
            self.LOCAL_MODEL_DIR.mkdir(parents=True)
        self.LOCAL_MODEL_DIR = str(self.LOCAL_MODEL_DIR)

        self.S3_RESOURCE_DIR = 'recommendation' # you can set your path
        self.S3_DATA_DIR = str(Path(self.S3_RESOURCE_DIR, self.LOCAL_DATA_DIR))
        self.S3_MODEL_DIR = str(Path(self.S3_RESOURCE_DIR, self.LOCAL_MODEL_DIR))
        
        # self.S3_BUCKET = S3(
        #     self.aws.s3.bucket,
        #     aws_access_key_id=self.aws.s3.access_key_id,
        #     aws_secret_access_key=self.aws.s3.access_key
        # )

        # self.SQS = SQS(

        #     aws_access_key_id = SQS_ACCESS_KEY,
        #     aws_secret_access_key = SQS_SECRET_KEY, 
        #     region_name = SQS_REGION)
        # )


Config = ProjectConfig(
    envvar_prefix="RUBICON",
    settings_files=[
        _CONFIG_PATH / "settings.yaml",
        _CONFIG_PATH / ".secrets.yaml",
    ],
    environments=True,
)


# export ENV_FOR_DYNACONF=production  # ENV_FOR_DYNACONF  vanni x dynaconfig ma aba yasle production ko credential use garxa, jun hamle set gareko xam mathi setting ma.
# export RUBICON_VARIABLE=value


# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load this files in the order.


# Challenging is how to set the credentials of prod(S3,SQS,database)

# One way is 
# export RUBICON_VARIABLE=value


# Another way is , tiniharule (hune vaneko machine ho last ma) kunai file ma rakhdeko hunxa tyo load garyara access garnuparyo
# import dotenv


# dotenv.load_dotenv('.env')
# s3_config = Config(
#     aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID_S3'),
#     aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY'),
#     region_name = os.environ.get('AWS_DEFAULT_REGION')
#
# )



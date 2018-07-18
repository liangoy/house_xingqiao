import connexion
import config

app = connexion.App(__name__, specification_dir='./')
app.add_api('api.yaml')
app.run(port=config.PORT)

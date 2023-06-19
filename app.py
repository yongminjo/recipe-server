from flask import Flask                       # 제발 flask run 하기전에 저장!!
from flask_restful import Api
from config import Config
from resources.recipe import RecipeListResource, RecipeResource
from resources.user import UserLoginResource, UserLogoutResource, UserRegisterResource, jwt_blocklist
from flask_jwt_extended import JWTManager

app = Flask(__name__)

# 환경변수 셋팅
app.config.from_object(Config)

# JWT 매니저 초기화
jwt = JWTManager(app)

# 로그아웃 된 토큰으로 요청하는 경우! 이 경우는 비정상적인 경우이므로,
# JWT가 알아서 처리하도록 코드를 작성해야한다!

@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in jwt_blocklist

# 플라스크 프레임워크에 JWT적용시킴.

api = Api(app)

# 경로와 API동작코드(Resource)를 연결한다.
api.add_resource( RecipeListResource , '/recipes')
api.add_resource( RecipeResource , '/recipes/<int:recipe_id>')
api.add_resource( UserRegisterResource , '/user/register')
api.add_resource( UserLoginResource , '/user/login')
api.add_resource( UserLogoutResource , '/user/logout')
# flask의 resource상속받은걸 알 수 있게 꼭 'Resource'를 붙여준다.


if __name__ == '__main__' :
    app.run()
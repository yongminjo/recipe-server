from flask_restful import Resource
from flask import request
import mysql.connector
from mysql.connector import Error
from mysql_connection import get_connection
from email_validator import validate_email, EmailNotValidError
from utils import check_password, hash_password
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
import datetime

# 로그아웃 관련 개발
## 로그아웃 된 토큰을 저장할 set을 만든다.
jwt_blocklist = set()
class UserLogoutResource(Resource) :
    # 골뱅이 붙여서 사용해야함. 
    @jwt_required()
    def delete(self):

        jti = get_jwt()['jti']
        print(jti)
        jwt_blocklist.add(jti) # 우리가 발급한 억세스 토큰

        return {'result' : 'success'}

class UserRegisterResource(Resource) :

    def post(self) :

        # {
        #     "username": "홍길동",
        #     "email": "abc@naver.com",
        #     "password": "1234"
        # }
        
        # 1. 클라이언트가 보낸 데이터를 받아준다.

        data = request.get_json()

        # 2. 이메일 주소 형식이 올바른지 확인한다.
        try :
            validate_email(data['email'])
        except EmailNotValidError as e:
            print(e)
            return {'result' : 'fail', 'error' : str(e)}, 400
        
        # 3. 비밀번호 길이가 유효한지 체크한다.
        # 만약에, 비번이 4자리 이상, 12자리 이하라고 한다면
        if len(data['password']) < 4 or len(data['password']) > 12 :
            return {'result' : 'fail', 'error' : '비번 길이 에러'}, 400
        # 여기서 체크하는 이유는 데이터의 무결성.

        # 4. 비밀번호를 암호화 한다. (이거 중요.)
        # 암호화방법1 암호화한 것을 원상복구 가능하게 할 수 있는거(양방향암호화(암호화-복호화))ㅣ비밀번호는 이방식 사용X
        # 방법2 단방향암호화(복호화X) - hash 

        # 4. 비밀번호를 암호화 한다.
        hashed_password = hash_password(data['password'])

        print(str(hashed_password))

        # 5. DB에 이미 회원정보가 있는지 확인한다.
        try :
            connection = get_connection()
            query = '''select *
                    from user
                    where email = %s;'''
            record = (data['email'] , )

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)

            result_list = cursor.fetchall()

            print(result_list)

            if len(result_list) == 1 :
                return {'result' : 'fail', 'error' : '이미 회원가입 한 사람'}, 400

            # 회원이 아니므로, 회원가입 코드를 작성한다.
            # DB에 저장한다.

            query = '''insert into user
                        (username, email, password)
                        values
                        (%s,%s,%s);'''
            record = (data['username'],
                      data['email'],
                      hashed_password)
            cursor = connection.cursor()
            cursor.execute(query, record)

            connection.commit()

            ### DB에 데이터를 insert한 후에,
            ### 그 인서트 된 행의 아이디를 가져오는 코드$!$!@#

            user_id = cursor.lastrowid

            cursor.close()
            connection.close()
        except Error as e:
            print(e)
            return {'result' : 'fail', 'error' : str(e)}, 500
        
        # create_access_token(user_id, expires_delta=datetime.timedelta(days=10))
        access_token = create_access_token(user_id)


        return {'result' : 'success', 'access_token' : access_token }, 200

# 로그인 관련 개발
class UserLoginResource(Resource) :
    def post(self) :

        # {
        #     "email": "abc@naver.com",
        #     "password": "1234"
        # }
        
        # 1. 클라이언트가 보낸 데이터를 받아준다.
        data = request.get_json()

        # 2. 이메일 주소로 DB에 select한다.
        try :
            connection = get_connection()
            query = '''select *
                    from user
                    where email = %s;'''
            record = (data['email'] ,)
                                        # 딕셔너리 타입으로 받아와야 데이터를 확인할 수 있다.
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)

            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            return {'result' : 'fail', 'error' : str(e)}, 500
        
        if len(result_list) == 0:
            return {'result' : 'fail', 'error':'회원가입한 사람 아님'}, 400
            
        # 3. 비밀번호가 일치하는지 확인한다.
        # 암호화된 비밀번호가 일치하는지 확인해야 함. (암호화 시켜놓고 확인.)
        print(result_list)

        check = check_password(data['password'], result_list[0]['password'])
        
        if check == False :
            return {'result' : 'fail', 'error' : '비밀번호 틀렸음'}, 400

        # 4. 클라이언트한테 데이터를 보내준다.

        access_token = create_access_token(result_list[0]['id'])

        return {'result' : 'success', 'access_token' : access_token}

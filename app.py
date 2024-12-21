from flask import Flask, request, jsonify  # Flask는 웹사이트를 만들 수 있는 도구, request는 사용자 요청을 받을 때 사용
import json  # 데이터를 주고받기 쉽게 변환하는 도구
import pymysql  # MySQL 데이터베이스와 연결할 수 있는 도구

import pandas as pd  # 데이터를 표 형태로 다룰 수 있는 도구
import numpy as np  # 숫자 데이터 계산을 쉽게 해주는 도구
from sklearn.metrics.pairwise import euclidean_distances  # 두 점 사이의 거리를 계산하는 도구
from sklearn.preprocessing import StandardScaler  # 데이터를 표준화(정리)하는 도구
import os


app = Flask(__name__)

DATABASE_URL = os.getenv('DATABASE_URL', 'default_url')
DATABASE_USER = os.getenv('DATABASE_USER', 'default_user')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'default_password')

#post 방식으로 movie_recomend URL일때 실행
@app.route('/movie/movie_recommend', methods=["POST"])
def movie_recommend():
    try:
        # 데이터베이스와 연결 설정
        # 데이터를 저장한 MySQL 데이터베이스에 연결하기 위한 정보 입력
        db = pymysql.connect(
            host=DATABASE_URL,  # 데이터베이스 주소 (AWS RDS)
            port=3306,  # MySQL이 사용하는 기본 포트 번호
            user=DATABASE_USER,  # 데이터베이스 사용자 이름
            passwd=DATABASE_PASSWORD ,  # 데이터베이스 비밀번호
            db='movie_db',  # 사용할 데이터베이스 이름
            charset='utf8'  # 데이터가 깨지지 않도록 UTF-8 인코딩 설정
        )

        # MySQL에서 모든 영화 데이터를 가져오는 SQL 명령어
        sql = "select * from movie_tbl;"

        # SQL 명령어 실행 결과를 표 형태의 데이터로 변환해서 movie_df에 저장
        movie_df = pd.read_sql(sql, db)

        # 각 영화의 줄거리 데이터를 숫자로 변환해서 새로운 칸에 저장
        movie_df.loc[:, "synopsis_vector_numpy"] = movie_df.loc[:, "synopsis_vector"].apply(
            lambda x: np.fromstring(x, dtype="float32")  # 줄거리 데이터를 숫자 배열로 바꾸는 작업
        )

        # 데이터를 정리(표준화)하기 위한 도구를 준비
        # 표준화: 데이터의 평균을 0으로, 데이터의 크기를 1로 맞추는 작업
        scaler = StandardScaler()

        # 데이터를 표준화하기 위한 계산 작업 (평균과 표준편차 계산)
        scaler.fit(np.array(movie_df["synopsis_vector_numpy"].tolist()))

        # 데이터를 표준화한 결과를 새로운 칸에 저장
        movie_df["synopsis_vector_numpy_scale"] = scaler.transform(
            np.array(movie_df["synopsis_vector_numpy"].tolist())
        ).tolist()

        # 영화들 간의 유사도를 계산하기 위한 거리(유클리드 거리)를 구함
        # 유클리드 거리: 두 영화 줄거리 간의 차이를 계산
        sim_score = euclidean_distances(
            movie_df["synopsis_vector_numpy_scale"].tolist(),
            movie_df["synopsis_vector_numpy_scale"].tolist()
        )

        # 계산된 거리를 표 형태로 변환 (행과 열이 영화 제목)
        sim_df = pd.DataFrame(data=sim_score)

        # 행(인덱스)에 영화 제목 추가
        sim_df.index = movie_df["title"]

        # 열(컬럼)에 영화 제목 추가
        sim_df.columns = movie_df["title"]
        # 사용자가 입력한 영화 제목 가져오기
        #title = request.form["title"]
         # React에서 보낸 데이터 받기
        data = request.get_json()
        title = data.get('title')  # 'title' 키로 데이터를 가져옴
        # 입력한 영화와 가장 비슷한 영화 10개를 찾음 (자신 제외)
        result = sim_df[title].sort_values()[1:11]

        # 찾은 영화들의 제목을 리스트로 변환
        result = result.index.to_list()

        # 리스트를 JSON 형식으로 변환 (웹에서 읽을 수 있도록)
        result_json = jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:

        db.close()
    # JSON 데이터를 결과로 반환
    return result_json

#get 방식으로 movie_latest URL일때 실행
#가장 최신 영화 10개를 Json 형태로 리턴
@app.route('/movie/movie_latest', methods=["GET"])
def movie_latest():
    try:
        # 데이터베이스와 연결 설정
        # 데이터를 저장한 MySQL 데이터베이스에 연결하기 위한 정보 입력
        # 데이터베이스와 연결 설정
        # 데이터를 저장한 MySQL 데이터베이스에 연결하기 위한 정보 입력
        db = pymysql.connect(
            host=DATABASE_URL,  # 데이터베이스 주소 (AWS RDS)
            port=3306,  # MySQL이 사용하는 기본 포트 번호
            user=DATABASE_USER,  # 데이터베이스 사용자 이름
            passwd=DATABASE_PASSWORD ,  # 데이터베이스 비밀번호
            db='movie_db',  # 사용할 데이터베이스 이름
            charset='utf8'  # 데이터가 깨지지 않도록 UTF-8 인코딩 설정
        )
        # 데이터베이스와 대화하는 '커서'를 생성 (데이터를 가져오거나 저장하는 역할)
        cursor = db.cursor(pymysql.cursors.DictCursor)

        # SQL 쿼리: 개봉일(open_date) 기준으로 최신 영화 10개를 가져옴
        query = "SELECT num,title,director,actor,synopsis,poster,open_date,degree,genre,country,movie_time FROM movie_tbl ORDER BY open_date DESC LIMIT 10"

        # SQL 쿼리 실행
        cursor.execute(query)

        # 실행 결과를 가져옴 (여러 개의 영화 정보를 리스트로 가져옴)
        result = cursor.fetchall()

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

    # 결과를 JSON 형태로 변환하여 반환
    return jsonify(result)


#get 방식으로 movie_popular URL일때 실행
#관람객 수가 가장 많은 영화 10개를 Json 형태로 리턴
@app.route('/movie/movie_popular', methods=["GET"])
def movie_popular():
    try:
        # 데이터베이스와 연결 설정
        # 데이터를 저장한 MySQL 데이터베이스에 연결하기 위한 정보 입력
        # 데이터베이스와 연결 설정
        # 데이터를 저장한 MySQL 데이터베이스에 연결하기 위한 정보 입력
        db = pymysql.connect(
            host=DATABASE_URL,  # 데이터베이스 주소 (AWS RDS)
            port=3306,  # MySQL이 사용하는 기본 포트 번호
            user=DATABASE_USER,  # 데이터베이스 사용자 이름
            passwd=DATABASE_PASSWORD ,  # 데이터베이스 비밀번호
            db='movie_db',  # 사용할 데이터베이스 이름
            charset='utf8'  # 데이터가 깨지지 않도록 UTF-8 인코딩 설정
        )
        # 커서 생성 (데이터베이스와 대화할 준비)
        cursor = db.cursor(pymysql.cursors.DictCursor)

        # SQL 쿼리: 관람객 수 또는 인기 점수(degree) 기준으로 상위 10개 영화 가져오기
        query = "SELECT num,title,director,actor,synopsis,poster,open_date,degree,genre,country,movie_time,box_office FROM movie_tbl ORDER BY box_office DESC LIMIT 10"

        # SQL 쿼리 실행
        cursor.execute(query)

        # 실행 결과를 가져옴
        result = cursor.fetchall()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

    # 결과를 JSON 형태로 변환하여 반환
    return jsonify(result)

#post 방식으로 get_movie URL일때 실행
#타이틀이 일치하는 영화 정보를 JSON으로 리턴
@app.route('/movie/get_movie', methods=["POST"])
def get_movie():

    # #request.form["title"] : 입력한 제목을 리턴
    # title = request.form["title"]
    # # 사용자가 입력한 영화 제목을 가져옴 (HTML 폼에서 "title"이라는 이름으로 입력된 값)
    # title = request.form["title"]
     # React에서 보낸 데이터 받기
    data = request.get_json()
    title = data.get('title')  # 'title' 키로 데이터를 가져옴
    try:
        # 데이터베이스와 연결 설정
        # 데이터를 저장한 MySQL 데이터베이스에 연결하기 위한 정보 입력
        # 데이터베이스와 연결 설정
        # 데이터를 저장한 MySQL 데이터베이스에 연결하기 위한 정보 입력
        db = pymysql.connect(
            host=DATABASE_URL,  # 데이터베이스 주소 (AWS RDS)
            port=3306,  # MySQL이 사용하는 기본 포트 번호
            user=DATABASE_USER,  # 데이터베이스 사용자 이름
            passwd=DATABASE_PASSWORD ,  # 데이터베이스 비밀번호
            db='movie_db',  # 사용할 데이터베이스 이름
            charset='utf8'  # 데이터가 깨지지 않도록 UTF-8 인코딩 설정
        )
        # 커서 생성
        cursor = db.cursor(pymysql.cursors.DictCursor)

        # SQL 쿼리: 제목이 사용자가 입력한 값과 일치하는 영화 찾기
        query = "SELECT num,title,director,actor,synopsis,poster,open_date,degree,genre,country,movie_time FROM movie_tbl WHERE title = %s"

        # SQL 쿼리 실행 (입력된 영화 제목을 쿼리에 전달)
        cursor.execute(query, (title,))

        # 결과를 가져옴 (일치하는 영화가 없으면 None 반환)
        result = cursor.fetchone()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


    # 결과가 있으면 JSON으로 변환해서 반환, 없으면 오류 메시지 반환
    return jsonify(result) if result else json.dumps({"error": "Movie not found"}, ensure_ascii=False)

    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
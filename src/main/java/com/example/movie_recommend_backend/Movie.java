package com.example.movie_recommend_backend;

import jakarta.persistence.*;
import lombok.*;


@Data
@Entity // 이 클래스가 데이터베이스 테이블과 연결됨을 나타냄
@Table(name = "movie_tbl") // 매핑할 테이블 이름 지정

public class Movie {

    // 영화정보 번호 (기본 키, 자동 증가)
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int num;

    // 영화 제목 (최대 100자)
    @Column(length = 100, nullable = false)
    private String title;

    // 감독 이름 (최대 100자)
    @Column(length = 100, nullable = false)
    private String director;

    // 배우 이름 (최대 100자)
    @Column(length = 100)
    private String actor;

    // 줄거리 (최대 1000자)
    @Column(length = 1000)
    private String synopsis;

    // 포스터 이미지 URL (최대 1000자)
    @Column(length = 1000)
    private String poster;

    // 개봉일 (날짜 형식) - 수정됨
    @Column(name = "open_date")
    private String openDate;

    // 영화 등급 (최대 100자)
    @Column(length = 100)
    private String degree;

    // 장르 (최대 100자)
    @Column(length = 100)
    private String genre;

    // 제작 국가 (최대 30자)
    @Column(length = 30)
    private String country;

    // 상영 시간 (최대 30자, 예: "120분")
    @Column(name = "movie_time", length = 30)
    private String movieTime;

    // 박스오피스 관람객 수 (정수형 데이터)
    @Column(name = "box_office")
    private int boxOffice;

}
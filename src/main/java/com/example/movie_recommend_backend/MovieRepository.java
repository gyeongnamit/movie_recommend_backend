package com.example.movie_recommend_backend;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository // 이 인터페이스가 저장소임을 나타내는 어노테이션

public interface MovieRepository extends JpaRepository<Movie, Integer> {

    // 박스오피스 관람객 수 기준 내림차순 정렬
    List<Movie> findAllByOrderByBoxOfficeDesc();

    // 개봉일 기준 내림차순 정렬
    List<Movie> findAllByOrderByOpenDateDesc();
}
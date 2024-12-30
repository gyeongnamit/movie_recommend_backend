package com.example.movie_recommend_backend;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpEntity;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import java.util.List;
import java.util.Map;
import org.springframework.beans.factory.annotation.Value;

@RestController // RESTful 컨트롤러를 나타내는 어노테이션

public class MovieController {
    // 의존성 주입 
    @Autowired
    private MovieRepository movieRepository;
    // Flask 서버 ip 설정
    @Value("${flask.ip}")
    String flaskIP;
    // 추천 영화 조회
    @PostMapping("/movie/movie_recommend")
    public List<String> getRecommendMovies(@RequestBody Map<String, String> request) {
        
        String flaskUrl="http://"+flaskIP+":5000/ai/ai_recommend";
        // HTTP 요청 헤더 설정
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        // 요청 본문에 사용자 입력 추가
        HttpEntity<Map<String, String>> entity = new HttpEntity<>(request, headers);

        // Flask 서버에 요청 보내기
        RestTemplate restTemplate = new RestTemplate();
        ResponseEntity<List> response = restTemplate.postForEntity(flaskUrl, entity, List.class);

        // Flask 서버에서 반환한 추천 영화 목록 반환
        return response.getBody();
    }

     // 최신 영화 10개 조회 (개봉일 기준 내림차순)
    @GetMapping("/movie/movie_latest")
    public List<Movie> getLatestMovies() {
        return movieRepository.findAllByOrderByOpenDateDesc().stream().limit(10).toList();
    }

    // 가장 인기 있는 영화 10개 조회 (관람객 수 기준 내림차순)
    @GetMapping("/movie/movie_popular")
    public List<Movie> getPopularMovies() {
        return movieRepository.findAllByOrderByBoxOfficeDesc().stream().limit(10).toList();
    }
}
package com.example.sf.Controller;

import com.example.sf.DTO.UserChoiceDTO;
import com.example.sf.Service.IdCheckService;
import lombok.RequiredArgsConstructor;
import lombok.extern.log4j.Log4j2;
import org.springframework.http.*;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.client.RestTemplate;

import java.security.Principal;
import java.util.HashMap;
import java.util.Map;

@Controller
@RequiredArgsConstructor
@Log4j2
public class ExerciseController {

    private final RestTemplate restTemplate = new RestTemplate();
    private final IdCheckService idCheckService;

    @GetMapping("/exercise")
    public String showExerciseForm() {
        return "exerciseForm"; // exerciseForm.html을 렌더링
    }

    @PostMapping("/exerciseResult")
    public String setExercise(@RequestParam("exercise1") String exerciseType,
                              @RequestParam("sets") String sets,
                              @RequestParam("reps") String reps,
                              Model model,
                              Principal principal) {

        Long userPk = idCheckService.IdCheck(principal);

        // 요청 데이터 생성
        Map<String, Object> requestData = new HashMap<>();
        try {
            // String to Integer 변환
            int exerciseTypeInt = Integer.parseInt(exerciseType);
            int setsInt = Integer.parseInt(sets);
            int repsInt = Integer.parseInt(reps);

            requestData.put("exercise_type", exerciseTypeInt);
            requestData.put("sets", setsInt);
            requestData.put("reps", repsInt);
        } catch (NumberFormatException e) {
            // 변환 오류가 발생한 경우 처리
            log.error("Invalid input for exercise parameters", e);
            return "error"; // 오류 페이지로 리디렉션 또는 오류 메시지 처리
        }

        // JSON 형식으로 데이터 전송하기 위한 설정
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestData, headers);
        // Flask 서버 URL
        String flaskUrl = "http://localhost:5000/set_exercise";

        // Flask 서버로 요청 보내기
        ResponseEntity<String> response = restTemplate.postForEntity(flaskUrl, entity, String.class);

        // 응답 로그 기록
        log.info("Response from Flask server: " + response.getBody());

        // 응답 결과에 따라 처리
        model.addAttribute("exerciseType", exerciseType);
        model.addAttribute("sets", sets);
        model.addAttribute("reps", reps);
        return "exerciseResult"; // View name for the result page
    }
}

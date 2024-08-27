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
    public String setExercise(@RequestParam("exercise1") Long exerciseType,
                              @RequestParam("sets") int sets,
                              @RequestParam("reps") int reps,
                              Model model,
                              Principal principal) {

        Long userPk = idCheckService.IdCheck(principal);

        // 요청 데이터 생성
        Map<String, Object> requestData = new HashMap<>();
        requestData.put("exercise_type", exerciseType);
        requestData.put("sets", sets);
        requestData.put("reps", reps);

        // JSON 형식으로 데이터 전송하기 위한 설정
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestData, headers);
        // Flask 서버 URL
        String flaskUrl = "http://localhost:5000/set_exercise";

        // Flask 서버로 요청 보내기
        ResponseEntity<Map> response = restTemplate.postForEntity(flaskUrl, entity, Map.class);

        Integer exerciseTypeInt = (Integer) response.getBody().get("exercise");
        Long exerciseTypeLong = exerciseTypeInt.longValue();

        UserChoiceDTO userChoiceDTO = new UserChoiceDTO();
        userChoiceDTO.setUserId(userPk);
        userChoiceDTO.setFitnessTypeId(exerciseTypeLong);
        log.info(userChoiceDTO);



        // Flask에서 받은 응답을 모델에 추가
        model.addAttribute("status", response.getBody().get("status"));
        model.addAttribute("exercise", response.getBody().get("exercise"));

        // 결과 페이지로 리다이렉트
        return "cam"; // exerciseResult.html을 렌더링
    }
}
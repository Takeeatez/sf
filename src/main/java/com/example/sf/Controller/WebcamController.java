package com.example.sf.Controller;

import com.example.sf.DTO.UserChoiceDTO;
import com.example.sf.Service.FitnessTypeService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

@Controller
@RequiredArgsConstructor
public class WebcamController {

    private final FitnessTypeService fitnessTypeService;


    @PostMapping("/saveExercise")
    public String saveExercise(@AuthenticationPrincipal String username,
                               @RequestParam("exercise1") Long fitId,
                               @RequestParam("reps") int reps,
                               @RequestParam("sets") int sets) {

        UserChoiceDTO userChoiceDTO = new UserChoiceDTO();
        userChoiceDTO.setUserName(username);
        userChoiceDTO.setFitnessTypeId(fitId);
        userChoiceDTO.setNum(reps);
        userChoiceDTO.setSets(sets);


        return "redirect:/setting"; // 설정 저장 후 이전 페이지로 리다이렉트
    }

    @GetMapping("/trymodel")
    public String trymodel() {
        return "trymodel";
    }

    // 웹캠 추가연결 매핑 예정
}
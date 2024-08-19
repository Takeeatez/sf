package com.example.sf.Controller;

import com.example.sf.DTO.ExerciseRecordDTO;
import com.example.sf.Service.CustomUserDetails;
import com.example.sf.Service.ExerciseRecordService;

// import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
//import com.example.sf.Service.CustomUserDetails;

import jakarta.servlet.http.HttpSession;

@Controller
public class MyPageController {

    private final ExerciseRecordService exerciseRecordService;

    public MyPageController(ExerciseRecordService exerciseRecordService) {
        this.exerciseRecordService = exerciseRecordService;
    }

    @GetMapping("/myPage")
    public String showMyPage(Model model) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        CustomUserDetails userDetails = (CustomUserDetails) authentication
                .getPrincipal();

        model.addAttribute("user", userDetails); // 모델에 '사용자 정보' 추가
        model.addAttribute("consecutiveLoginDays", userDetails.getConsecutiveLoginDays()); // 모델에 '연속 로그인 일수' 추가
        model.addAttribute("exerciseRecord", new ExerciseRecordDTO()); // 모델에 ExerciseRecordDTO 객체 추가

        return "myPage";
    }

    @PostMapping("/myPage")
    public String saveExerciseType(@ModelAttribute("exerciseRecord") ExerciseRecordDTO exerciseRecord,
            HttpSession session) {
        // 세션에 저장 (유지하기 위해)
        session.setAttribute("exerciseRecord", exerciseRecord);

        // 운동 종목을 DB에 저장
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String userId = authentication.getName();

        exerciseRecordService.saveExerciseType(exerciseRecord.getExerciseType(), userId);

        return "redirect:/setting";
    }
}

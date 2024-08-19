package com.example.sf.Controller;

import com.example.sf.DTO.ExerciseRecordDTO;
import com.example.sf.Service.ExerciseRecordService;

import jakarta.servlet.http.HttpSession;

import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.security.core.Authentication;

@Controller
public class WebcamController {

    private final ExerciseRecordService exerciseRecordService;

    public WebcamController(ExerciseRecordService exerciseRecordService) {
        this.exerciseRecordService = exerciseRecordService;
    }

    @GetMapping("/webcam")
    public String showWebcamPage(Model model, HttpSession session) {
        ExerciseRecordDTO exerciseRecord = (ExerciseRecordDTO) session.getAttribute("exerciseRecord");
        if (exerciseRecord == null) {
            exerciseRecord = new ExerciseRecordDTO(); // 초기화
        }
        model.addAttribute("exerciseRecord", exerciseRecord);
        return "webcam";
    }

    @PostMapping("/webcam")
    public String saveExerciseDetails(@ModelAttribute("exerciseRecord") ExerciseRecordDTO exerciseRecord,
            HttpSession session) {
        ExerciseRecordDTO existingRecord = (ExerciseRecordDTO) session.getAttribute("exerciseRecord");
        existingRecord.setExerciseDate(exerciseRecord.getExerciseDate());
        existingRecord.setExerciseTime(exerciseRecord.getExerciseTime());
        existingRecord.setAchievementRate(exerciseRecord.getAchievementRate());

        // 운동 날짜, 시간, 달성률을 DB에 저장
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String userId = authentication.getName();

        exerciseRecordService.saveExerciseDetails(existingRecord.getExerciseDate(), existingRecord.getExerciseTime(),
                existingRecord.getAchievementRate(), userId);

        return "redirect:/main";
    }

}

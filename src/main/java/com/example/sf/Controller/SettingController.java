package com.example.sf.Controller;

import com.example.sf.DTO.ExerciseRecordDTO;
import com.example.sf.Service.ExerciseRecordService;

import jakarta.servlet.http.HttpSession;

//import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.security.core.Authentication;

@Controller
public class SettingController {

    private final ExerciseRecordService exerciseRecordService;

    public SettingController(ExerciseRecordService exerciseRecordService) {
        this.exerciseRecordService = exerciseRecordService;
    }

    @GetMapping("/setting")
    public String showSettingPage(Model model, HttpSession session) {
        ExerciseRecordDTO exerciseRecord = (ExerciseRecordDTO) session.getAttribute("exerciseRecord");
        if (exerciseRecord == null) {
            exerciseRecord = new ExerciseRecordDTO(); // 초기화
        }
        model.addAttribute("exerciseRecord", exerciseRecord);
        return "setting";
    }

    @PostMapping("/setting")
    public String saveRepsAndSets(@ModelAttribute("exerciseRecord") ExerciseRecordDTO exerciseRecord,
            HttpSession session) {
        ExerciseRecordDTO existingRecord = (ExerciseRecordDTO) session.getAttribute("exerciseRecord");
        if (existingRecord != null) {
            existingRecord.setReps(exerciseRecord.getReps());
            existingRecord.setSets(exerciseRecord.getSets());
        } else {
            existingRecord = exerciseRecord;
        }

        session.setAttribute("exerciseRecord", existingRecord);

        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String userId = authentication.getName();

        exerciseRecordService.saveRepsAndSets(existingRecord.getReps(), existingRecord.getSets(), userId);

        return "redirect:/webcam";
    }
}

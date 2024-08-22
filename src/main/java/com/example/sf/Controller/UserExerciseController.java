package com.example.sf.Controller;

import com.example.sf.Entity.FitnessTypeEntity;
import com.example.sf.Service.FitnessTypeService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

import java.util.List;

@Controller
public class UserExerciseController {
    @Autowired
    private FitnessTypeService fitnessTypeService;

    @GetMapping("/exercise")
    public String showExercisePage(Model model) {
        List<FitnessTypeEntity> fitnessTypes = fitnessTypeService.getAllFitnessTypes();
        model.addAttribute("exercises", fitnessTypes);
        return "exercise";
    }
}

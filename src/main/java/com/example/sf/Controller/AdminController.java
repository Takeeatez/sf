package com.example.sf.Controller;

import com.example.sf.Entity.FitnessTypeEntity;
import com.example.sf.Service.AdminService;
import com.example.sf.Service.FitnessTypeService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Controller
public class AdminController {

    @Autowired
    private AdminService adminService;
    private FitnessTypeService fitnessTypeService;

    @GetMapping("/admin")
    public String admin(){
        return "admin";
    }

    @GetMapping("/dashboard")
    public String showAdminDashboard(Model model) {
        List<FitnessTypeEntity> exercises = fitnessTypeService.getAllFitnessTypes();
        model.addAttribute("exercises", exercises);
        return "adminDashboard";
    }

    @PostMapping("/addExercise")
    public String addExercise(@ModelAttribute FitnessTypeEntity exercise) {
        fitnessTypeService.saveExercise(exercise);
        return "redirect:/admin/dashboard";
    }

    @PostMapping("/updateExercise")
    @ResponseBody
    public ResponseEntity<?> updateExercise(@RequestBody FitnessTypeEntity exercise) {
        FitnessTypeEntity updatedExercise = fitnessTypeService.updateExercise(exercise);
        if (updatedExercise != null) {
            return ResponseEntity.ok().body("{\"success\": true}");
        } else {
            return ResponseEntity.status(400).body("{\"success\": false}");
        }
    }

    @DeleteMapping("/deleteExercise/{fitId}")
    @ResponseBody
    public ResponseEntity<?> deleteExercise(@PathVariable int fitId) {
        boolean success = fitnessTypeService.deleteExercise(fitId);
        if (success) {
            return ResponseEntity.ok().body("{\"success\": true}");
        } else {
            return ResponseEntity.status(400).body("{\"success\": false}");
        }
    }
}

package com.example.sf.Controller;

import com.example.sf.DTO.UserDTO;
import com.example.sf.Entity.FitnessTypeEntity;
import com.example.sf.Service.AdminService;
import com.example.sf.Service.FitnessTypeService;
import com.example.sf.Service.UserService;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Controller
public class AdminController {

    private final AdminService adminService;
    private final FitnessTypeService fitnessTypeService;
    private final UserService userService;

    public AdminController(AdminService adminService, FitnessTypeService fitnessTypeService, UserService userService) {
        this.adminService = adminService;
        this.fitnessTypeService = fitnessTypeService;
        this.userService = userService;
    }

    @GetMapping("/admin")
    public String adminDashboard(Model model) {
        // 모든 유저 정보 조회
        List<UserDTO> users = userService.getAllUsers();
        model.addAttribute("users", users);

        // 모든 운동 정보 조회
        List<FitnessTypeEntity> exercises = fitnessTypeService.getAllFitnessTypes();
        model.addAttribute("exercises", exercises);
        return "admin";
    }

    @PostMapping("/admin/addExercise")
    public String addExercise(@ModelAttribute FitnessTypeEntity exercise) {
        fitnessTypeService.saveExercise(exercise);
        return "redirect:/admin"; // 추가 후 관리자 대시보드로 리다이렉트
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

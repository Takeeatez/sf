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

    // 운동 추가
    @PostMapping("/admin/addExercise")
    public String addExercise(@ModelAttribute FitnessTypeEntity exercise) {
        fitnessTypeService.saveExercise(exercise);
        return "redirect:/admin"; // 추가 후 관리자 대시보드로 리다이렉트
    }

    // 운동 업데이트
    @PostMapping("/admin/updateExercise/{fitId}")
    public String updateExercise(@ModelAttribute FitnessTypeEntity exercise, @PathVariable("fitId") int fitId) {
        FitnessTypeEntity updatedExercise = fitnessTypeService.updateExercise(exercise);
        return "redirect:/admin";
    }

    // 운동 삭제
    @PostMapping("/admin/deleteExercise/{fitId}")
    public String deleteExercise(@PathVariable int fitId) {
        fitnessTypeService.deleteExercise(fitId);
        return "redirect:/admin";
    }
}

package com.example.sf.Controller;

import com.example.sf.DTO.UserDTO;
import com.example.sf.Entity.FitnessTypeEntity;
import com.example.sf.Service.FitnessTypeService;
import com.example.sf.Service.UserService;
import lombok.RequiredArgsConstructor;
import lombok.extern.log4j.Log4j2;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;

import java.util.List;

@Controller
@RequiredArgsConstructor
@Log4j2
public class UserController {

    private final UserService userService;
    private FitnessTypeService fitnessTypeService;

    @GetMapping({ "/", "/login" })
    public String login(Model model) {
        return "login";
    }

    @GetMapping("/register")
    public String showRegistrationForm(Model model) {
        model.addAttribute("user", new UserDTO());
        return "register";
    }

    @PostMapping("/register")
    public String registerUser(UserDTO userDTO) {
        userService.createUser(userDTO);
        return "redirect:/login";
    }


    @GetMapping("/myPage")
    public String showMyPage(Model model) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String currentUserName = authentication.getName();

        UserDTO userDTO = userService.getUserByUserName(currentUserName);
        // 이름 받아옴
        model.addAttribute("userName", userDTO.getUserName());
        // 가입날짜 받아옴
        model.addAttribute("createdAt", userDTO.getCreatedAt());

        return "myPage";
    }

    // aboutUs 매핑
    @GetMapping("/aboutUs")
    public String AboutUs() {
        return "aboutUs";
    }

    // setting 매핑
    @GetMapping("/setting")
    public String setting(Model model) {
        // 운동 리스트 불러옴
        List<FitnessTypeEntity> fitnessTypes = fitnessTypeService.getAllFitnessTypes();
        model.addAttribute("exercises", fitnessTypes);
        return "setting";
    }

    @GetMapping("/main")
    public String main() {
        return "main";
    }
}
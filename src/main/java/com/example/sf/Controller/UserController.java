package com.example.sf.Controller;

import com.example.sf.DTO.UserDTO;
import com.example.sf.Entity.FitnessTypeEntity;
import com.example.sf.Service.FitnessTypeService;
import com.example.sf.Service.UserService;
import lombok.RequiredArgsConstructor;
import lombok.extern.log4j.Log4j2;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;

import java.security.Principal;
import java.util.List;

@Controller
@RequiredArgsConstructor
@Log4j2
public class UserController {

    private final UserService userService;
    @Autowired
    private FitnessTypeService fitnessTypeService;


    @GetMapping({"/", "/test"})
    public String test(){
        return "test";
    }

    @GetMapping("/login")
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
    public String showMyPage(Principal principal, Model model) {
        // Principal로부터 사용자 이름 가져오기
        String userName = principal.getName();

        // 사용자 이름으로 사용자 정보를 가져옴
        String userName1 = userService.getUserByUserName(userName);
        UserDTO userDTO = userService.getUserInfo(userName);

        // 모델에 사용자 정보 추가
        model.addAttribute("userName", userName1);
        model.addAttribute("joinDate", userDTO.getJoinDate());

        // 마이페이지로 이동
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
    public String main(Principal principal, Model model) {
        // Principal로부터 사용자 이름 가져오기
        String userName = principal.getName();

        // 사용자 이름으로 사용자 정보를 가져옴
        String userName1 = userService.getUserByUserName(userName);
        model.addAttribute("userName", userName1);

        return "main";
    }
}
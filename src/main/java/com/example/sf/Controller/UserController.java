package com.example.sf.Controller;

import com.example.sf.DTO.UserDTO;
import com.example.sf.Service.UserService;
import lombok.RequiredArgsConstructor;
import lombok.extern.log4j.Log4j2;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;

@Controller
@RequiredArgsConstructor
@Log4j2
public class UserController {

    private final UserService userService;

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

    @GetMapping("/main")
    public String main() {
        return "main";
    }

    // @GetMapping("/myPage")
    // public String showMyPagePage() {
    // return "myPage";
    // }

    @GetMapping("/setting")
    public String showSettingPage() {
        return "setting";
    }

    @GetMapping("/webcam")
    public String showMWebcamPage() {
        return "webcam";
    }
}
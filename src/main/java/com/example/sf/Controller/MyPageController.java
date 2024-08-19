package com.example.sf.Controller;

import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import com.example.sf.Service.CustomUserDetails;

@Controller
public class MyPageController {
    @GetMapping("/myPage")
    public String showMyPage(Model model) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        CustomUserDetails userDetails = (CustomUserDetails) authentication
                .getPrincipal();

        model.addAttribute("user", userDetails); // 모델에 '사용자 정보' 추가
        model.addAttribute("consecutiveLoginDays", userDetails.getConsecutiveLoginDays()); // 모델에 '연속 로그인 일수' 추가

        return "myPage";
    }
}

package com.example.sf.Controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class MyPageController {

    @GetMapping("/myPage")
    public String showMyPage(Model model) {
        model.addAttribute("attributeName", "attributeValue");
        return "myPage"; // myPage.html 템플릿을 반환
    }
}

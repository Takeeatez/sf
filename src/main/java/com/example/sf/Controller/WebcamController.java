package com.example.sf.Controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class WebcamController {

    @GetMapping("/trymodel")
    public String trymodel() {
        return "trymodel";
    }

    // 웹캠 추가연결 매핑 예정
}

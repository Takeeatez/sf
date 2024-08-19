package com.example.sf.Controller;

import com.example.sf.DTO.FitRecordDTO;
import com.example.sf.Service.CustomUserDetails;
import com.example.sf.Service.FitRecordService;

// import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
//import com.example.sf.Service.CustomUserDetails;

import jakarta.servlet.http.HttpSession;

@Controller
public class MyPageController {

    private final FitRecordService fitRecordService;

    public MyPageController(FitRecordService fitRecordService) {
        this.fitRecordService = fitRecordService;
    }

    @GetMapping("/myPage")
    public String showMyPage(Model model) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        CustomUserDetails userDetails = (CustomUserDetails) authentication
                .getPrincipal();

        model.addAttribute("user", userDetails); // 모델에 '사용자 정보' 추가
        model.addAttribute("consecutiveLoginDays", userDetails.getConsecutiveLoginDays()); // 모델에 '연속 로그인 일수' 추가
        model.addAttribute("fitRecord", new FitRecordDTO()); // 모델에 FitRecordDTO 객체 추가

        return "myPage";
    }

    @PostMapping("/myPage")
    public String saveFitType(@ModelAttribute("fitRecord") FitRecordDTO fitRecord,
            HttpSession session) {
        // 세션에 저장 (유지하기 위해)
        session.setAttribute("fitRecord", fitRecord);

        // 운동 종목을 DB에 저장
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String userId = authentication.getName();

        fitRecordService.saveFitType(fitRecord.getFitType(), userId);

        return "redirect:/setting";
    }
}

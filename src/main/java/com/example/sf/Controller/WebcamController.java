package com.example.sf.Controller;

import com.example.sf.DTO.FitRecordDTO;
import com.example.sf.Service.FitRecordService;

import jakarta.servlet.http.HttpSession;

import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.security.core.Authentication;

@Controller
public class WebcamController {

    private final FitRecordService fitRecordService;

    public WebcamController(FitRecordService fitRecordService) {
        this.fitRecordService = fitRecordService;
    }

    @GetMapping("/webcam")
    public String showWebcamPage(Model model, HttpSession session) {
        FitRecordDTO fitRecord = (FitRecordDTO) session.getAttribute("fitRecord");
        if (fitRecord == null) {
            fitRecord = new FitRecordDTO(); // 초기화
        }
        model.addAttribute("fitRecord", fitRecord);
        return "webcam";
    }

    @PostMapping("/webcam")
    public String saveFitDetails(@ModelAttribute("fitRecord") FitRecordDTO fitRecord,
            HttpSession session) {
        FitRecordDTO existingRecord = (FitRecordDTO) session.getAttribute("fitRecord");
        existingRecord.setFitDate(fitRecord.getFitDate());
        existingRecord.setFitTime(fitRecord.getFitTime());
        existingRecord.setRate(fitRecord.getRate());

        // 운동 날짜, 시간, 달성률을 DB에 저장
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String userId = authentication.getName();

        fitRecordService.saveFitDetails(existingRecord.getFitDate(), existingRecord.getFitTime(),
                existingRecord.getRate(), userId);

        return "redirect:/main";
    }

}

package com.example.sf.Controller;

import com.example.sf.DTO.FitRecordDTO;
import com.example.sf.Service.FitRecordService;

import jakarta.servlet.http.HttpSession;

//import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.security.core.Authentication;

@Controller
public class SettingController {

    private final FitRecordService fitRecordService;

    public SettingController(FitRecordService fitRecordService) {
        this.fitRecordService = fitRecordService;
    }

    @GetMapping("/setting")
    public String showSettingPage(Model model, HttpSession session) {
        FitRecordDTO fitRecord = (FitRecordDTO) session.getAttribute("fitRecord");
        if (fitRecord == null) {
            fitRecord = new FitRecordDTO(); // 초기화
        }
        model.addAttribute("fitRecord", fitRecord);
        return "setting";
    }

    @PostMapping("/setting")
    public String saveCountsAndSets(@ModelAttribute("fitRecord") FitRecordDTO fitRecord,
            HttpSession session) {
        FitRecordDTO existingRecord = (FitRecordDTO) session.getAttribute("fitRecord");
        if (existingRecord != null) {
            existingRecord.setCounts(fitRecord.getCounts());
            existingRecord.setSets(fitRecord.getSets());
        } else {
            existingRecord = fitRecord;
        }

        session.setAttribute("fitRecord", existingRecord);

        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String userId = authentication.getName();

        fitRecordService.saveCountsAndSets(existingRecord.getCounts(), existingRecord.getSets(), userId);

        return "redirect:/webcam";
    }
}

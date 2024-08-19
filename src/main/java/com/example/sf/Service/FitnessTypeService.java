package com.example.sf.Service;

import com.example.sf.Entity.FitnessTypeEntity;
import com.example.sf.Repository.FitnessTypeRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class FitnessTypeService {

    @Autowired
    private FitnessTypeRepository fitnessTypeRepository;

    public List<FitnessTypeEntity> getAllFitnessTypes() {
        return fitnessTypeRepository.findAll();
    }

    public void saveExercise(FitnessTypeEntity exercise) {
        fitnessTypeRepository.save(exercise);
    }

    public FitnessTypeEntity updateExercise(FitnessTypeEntity exercise) {
        return fitnessTypeRepository.save(exercise);
    }

    public boolean deleteExercise(int fitId) {
        try {
            fitnessTypeRepository.deleteById(fitId);
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}

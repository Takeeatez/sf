package com.example.sf.Service;

import com.example.sf.Entity.FitnessTypeEntity;
import com.example.sf.Repository.FitnessTypeRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class FitnessTypeService {

    private final FitnessTypeRepository fitnessTypeRepository;

    public FitnessTypeService(FitnessTypeRepository fitnessTypeRepository) {
        this.fitnessTypeRepository = fitnessTypeRepository;
    }

    public FitnessTypeEntity saveExercise(FitnessTypeEntity fitnessTypeEntity) {
        return fitnessTypeRepository.save(fitnessTypeEntity);
    }

    public FitnessTypeEntity updateExercise(FitnessTypeEntity fitnessTypeEntity) {
        Optional<FitnessTypeEntity> existingEntity = fitnessTypeRepository.findById(fitnessTypeEntity.getFitId());
        if (existingEntity.isPresent()) {
            FitnessTypeEntity updatedEntity = existingEntity.get();
            updatedEntity.setName(fitnessTypeEntity.getName());
            updatedEntity.setDescription(fitnessTypeEntity.getDescription());
            return fitnessTypeRepository.save(updatedEntity);
        }
        return null;
    }

    public boolean deleteExercise(int fitId) {
        Optional<FitnessTypeEntity> existingEntity = fitnessTypeRepository.findById(fitId);
        if (existingEntity.isPresent()) {
            fitnessTypeRepository.delete(existingEntity.get());
            return true;
        }
        return false;
    }

    public List<FitnessTypeEntity> getAllFitnessTypes() {
        return fitnessTypeRepository.findAll();
    }

    public FitnessTypeEntity getExerciseById(int fitId) {
        return fitnessTypeRepository.findById(fitId).orElse(null);
    }
}

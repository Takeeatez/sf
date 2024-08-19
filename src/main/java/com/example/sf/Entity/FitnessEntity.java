package com.example.sf.Entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import java.util.List;

@Getter
@Setter
@Entity
@Table(name = "Fitness")
public class FitnessEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer fitnum;

    @Column(length = 255)
    private String name;

    @Column(length = 255)
    private String description;

    @ManyToOne
    @JoinColumn(name = "fitId", nullable = false)
    private FitnessTypeEntity fitnessType;

    @OneToMany(mappedBy = "fitness", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<UserChoiceEntity> choices;
}

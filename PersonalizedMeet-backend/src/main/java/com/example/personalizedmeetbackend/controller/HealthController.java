package com.example.personalizedmeetbackend.controller;

import java.time.LocalDateTime;
import java.util.Map;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class HealthController {

    @GetMapping("/health")
    public Map<String, Object> healthCheck() {
        return Map.of(
                "status", "UP",
                "message", "PersonalizedMeet backend is running",
                "timestamp", LocalDateTime.now()
        );
    }
}

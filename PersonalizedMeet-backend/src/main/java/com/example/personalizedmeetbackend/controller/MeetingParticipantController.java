package com.example.personalizedmeetbackend.controller;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.personalizedmeetbackend.dto.MeetingParticipantRequest;
import com.example.personalizedmeetbackend.dto.MeetingParticipantResponse;
import com.example.personalizedmeetbackend.dto.MeetingParticipantRoleUpdateRequest;
import com.example.personalizedmeetbackend.service.MeetingParticipantService;

import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/meeting-participants")
public class MeetingParticipantController {

    private final MeetingParticipantService meetingParticipantService;

    public MeetingParticipantController(MeetingParticipantService meetingParticipantService) {
        this.meetingParticipantService = meetingParticipantService;
    }

    @PostMapping
    public ResponseEntity<MeetingParticipantResponse> addParticipant(
            @Valid @RequestBody MeetingParticipantRequest request
    ) {
        MeetingParticipantResponse response = meetingParticipantService.addParticipant(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping("/meeting/{meetingId}")
    public ResponseEntity<List<MeetingParticipantResponse>> getParticipantsByMeeting(
            @PathVariable Long meetingId
    ) {
        return ResponseEntity.ok(meetingParticipantService.getParticipantsByMeeting(meetingId));
    }

    @GetMapping("/{id}")
    public ResponseEntity<MeetingParticipantResponse> getParticipantById(@PathVariable Long id) {
        return ResponseEntity.ok(meetingParticipantService.getParticipantById(id));
    }

    @PutMapping("/{id}/role")
    public ResponseEntity<MeetingParticipantResponse> updateParticipantRole(
            @PathVariable Long id,
            @Valid @RequestBody MeetingParticipantRoleUpdateRequest request
    ) {
        return ResponseEntity.ok(meetingParticipantService.updateParticipantRole(id, request));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> removeParticipant(@PathVariable Long id) {
        meetingParticipantService.removeParticipant(id);
        return ResponseEntity.noContent().build();
    }
}

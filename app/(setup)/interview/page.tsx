"use client"

import React from "react";
import { Flex, Box, Text, Button } from "@chakra-ui/react"
import { Container } from '@chakra-ui/react'
import { useConfigState } from "../_state/configState"
import HostingStep from '../_components/HostingStep'
import AuthStep from '../_components/AuthStep'
import LLMStep from '../_components/LLMStep'
import Configurations from '../_components/Configurations'


export default function InterviewPage() {
  const {
    configState,
    setConfigState,
    updateHostingType,
    updateGithubClientId,
    updateGithubClientSecret,
    addLLMConfig: addLLMConfigAction,
    removeLLMConfig: removeLLMConfigAction,
  } = useConfigState();
  const currentStep = configState.currentStep;

  const steps = [
    { title: 'Hosting Configuration', description: 'Choose how you want to deploy' },
    { title: 'Authentication Setup', description: 'Configure GitHub OAuth' },
    { title: 'LLM Configuration', description: 'Setup AI providers' },
    { title: 'Configuration', description: 'Download your .env file' }
  ]


  const addLLMConfig = () => {
    addLLMConfigAction();
  }

  const removeLLMConfig = (index: number) => {
    removeLLMConfigAction(index);
  }

  const generateEnvFile = () => {
    let envContent = '# Generated Environment Configuration\n\n'
    envContent += `HOSTING_TYPE=${configState.hostingType}\n\n`
    if (configState.hostingType === 'multi-user') {
      envContent += '# GitHub OAuth Configuration\n'
      envContent += `GITHUB_CLIENT_ID=${configState.githubClientId}\n`
      envContent += `GITHUB_CLIENT_SECRET=${configState.githubClientSecret}\n\n`
    }
    envContent += '# LLM Provider Configurations\n'
    configState.llmConfigs.forEach((config) => {
      const providerKey = config.provider.toUpperCase()
      envContent += `${providerKey}_API_KEY=${config.apiKey}\n`
      envContent += `${providerKey}_MODEL=${config.model}\n`
    })
    return envContent
  }

  const downloadEnvFile = () => {
    const content = generateEnvFile()
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = '.env'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }


  const renderStepContent = (step: number) => {
    switch (step) {
      case 1:
        return (
          <HostingStep
            hostingType={configState.hostingType}
            setHostingType={updateHostingType}
          />
        )
      case 2:
        return (
          <AuthStep
            hostingType={configState.hostingType}
            githubClientId={configState.githubClientId}
            githubClientSecret={configState.githubClientSecret}
            setGithubClientId={updateGithubClientId}
            setGithubClientSecret={updateGithubClientSecret}
          />
        )
      case 3:
        return (
          <LLMStep
            selectedProvider={currentStep.selectedProvider}
            setSelectedProvider={provider =>
              setConfigState(prev => ({
                ...prev,
                currentStep: { ...prev.currentStep, selectedProvider: provider }
              }))
            }
            selectedModel={currentStep.selectedModel}
            setSelectedModel={model =>
              setConfigState(prev => ({
                ...prev,
                currentStep: { ...prev.currentStep, selectedModel: model }
              }))
            }
            apiKey={currentStep.apiKey}
            setApiKey={key =>
              setConfigState(prev => ({
                ...prev,
                currentStep: { ...prev.currentStep, apiKey: key }
              }))
            }
            llmConfigs={configState.llmConfigs}
            addLLMConfig={addLLMConfig}
            removeLLMConfig={removeLLMConfig}
            downloadEnvFile={downloadEnvFile}
          />
        )
      case 4:
        return (
          <Configurations downloadEnvFile={downloadEnvFile} />
        )
      default:
        return null
    }
  }

  return (
    <Container maxW="4xl" py={8}>
      <Flex align="flex-start" justify="center" mb={8} gap={0}>
        {steps.map((stepObj, index) => (
          <React.Fragment key={stepObj.title}>
            <Flex direction="column" align="center" justify="center" minW="60px">
              <Box
                w="36px"
                h="36px"
                borderRadius="full"
                bg={index + 1 <= currentStep.step ? "fg" : "bg.muted"}
                color={index + 1 <= currentStep.step ? "bg" : "fg.muted"}
                display="flex"
                alignItems="center"
                justifyContent="center"
                fontWeight="bold"
                fontSize="xl"
                borderWidth="0"
                transition="background 0.2s, color 0.2s, border 0.2s"
                boxSizing="border-box"
                boxShadow={index + 1 === currentStep.step ? "md" : "none"}
              >
                {index + 1}
              </Box>
              <Text
                mt={2}
                fontSize="sm"
                color={index + 1 === currentStep.step ? "fg" : "fg.subtle"}
                fontWeight={index + 1 === currentStep.step ? "bold" : "normal"}
                textAlign="center"
                maxW="120px"
                lineHeight="1.2"
                minH="32px"
                display="flex"
                alignItems="center"
                justifyContent="center"
              >
                {stepObj.title}
              </Text>
            </Flex>
            {index < steps.length - 1 && (
              <Box
                w="40px"
                h="2px"
                alignSelf="center"
                bg={index + 1 < currentStep.step ? "fg" : "gray.200"}
                mx={2}
                borderRadius="md"
                transition="background 0.2s"
              />
            )}
          </React.Fragment>
        ))}
      </Flex>
      {/* Step Content */}
      <div>
        {renderStepContent(currentStep.step)}
      </div>
      {/* Navigation */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 32 }}>
        <Button
          variant="outline"
          onClick={() =>
            setConfigState(prev => ({
              ...prev,
              currentStep: {
                ...prev.currentStep,
                step: Math.max(1, prev.currentStep.step - 1)
              }
            }))
          }
          disabled={currentStep.step === 1}
        >
          ← Previous
        </Button>
        <span>Step {currentStep.step} of {steps.length}</span>
        {currentStep.step < steps.length ? (
          <Button
            variant="outline"
            onClick={() =>
              setConfigState(prev => ({
                ...prev,
                currentStep: {
                  ...prev.currentStep,
                  step: prev.currentStep.step + 1
                }
              }))
            }
            disabled={
              (currentStep.step === 1 && !configState.hostingType) ||
              (currentStep.step === 2 && configState.hostingType === 'multi-user' &&
                (!configState.githubClientId || !configState.githubClientSecret)) ||
              (currentStep.step === 3 && configState.llmConfigs.length === 0)
            }
          >
            Next →
          </Button>
        ) : (
          <Button
            onClick={() => {
              // Setup complete
            }}
          >
            Complete Setup
          </Button>
        )}
      </div>
      {/* Configuration step */}
      {currentStep.step > steps.length && (
        <Configurations downloadEnvFile={downloadEnvFile} />
      )}
    </Container>
  )
}
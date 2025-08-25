"use client"

import { useState } from 'react'
import {
  Box,
  Container,
  VStack,
  HStack,
  Text,
  Button,
  Input,
  Combobox,
  createToaster,
  createListCollection
} from '@chakra-ui/react'

const toaster = createToaster({
  placement: 'top',
})

// Sample data for LLM providers and models
const LLM_PROVIDERS = [
  {
    id: 'openai',
    name: 'OpenAI',
    models: [
      { id: 'gpt-4o', name: 'GPT-4o' },
      { id: 'gpt-4o-mini', name: 'GPT-4o Mini' },
      { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo' }
    ]
  },
  {
    id: 'anthropic',
    name: 'Anthropic',
    models: [
      { id: 'claude-3-5-sonnet', name: 'Claude 3.5 Sonnet' },
      { id: 'claude-3-haiku', name: 'Claude 3 Haiku' }
    ]
  },
  {
    id: 'google',
    name: 'Google',
    models: [
      { id: 'gemini-pro', name: 'Gemini Pro' },
      { id: 'gemini-pro-vision', name: 'Gemini Pro Vision' }
    ]
  }
]

// Sample repository data
const SAMPLE_REPOS = [
  { id: 1, name: 'my-project', fullName: 'user/my-project', branches: ['main', 'develop', 'feature/auth'] },
  { id: 2, name: 'web-app', fullName: 'user/web-app', branches: ['main', 'staging'] },
  { id: 3, name: 'api-server', fullName: 'user/api-server', branches: ['main', 'v2', 'hotfix'] }
]

interface SetupData {
  hostingType: 'self' | 'multi-user' | ''
  githubClientId: string
  githubClientSecret: string
  llmConfigs: Array<{
    provider: string
    model: string
    apiKey: string
  }>
  selectedRepos: Array<{
    repoId: number
    branch: string
  }>
}

export default function SetupPage() {
  const [currentStep, setCurrentStep] = useState(1)
  const [setupData, setSetupData] = useState<SetupData>({
    hostingType: '',
    githubClientId: '',
    githubClientSecret: '',
    llmConfigs: [],
    selectedRepos: []
  })
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [selectedProvider, setSelectedProvider] = useState('')
  const [selectedModel, setSelectedModel] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [selectedRepo, setSelectedRepo] = useState('')
  const [selectedBranch, setSelectedBranch] = useState('')

  const steps = [
    { title: 'Hosting Configuration', description: 'Choose how you want to deploy' },
    { title: 'Authentication Setup', description: 'Configure GitHub OAuth' },
    { title: 'LLM Configuration', description: 'Setup AI providers' },
    { title: 'Repository Selection', description: 'Choose your repositories' }
  ]

  const handleNext = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrev = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const addLLMConfig = () => {
    if (selectedProvider && selectedModel && apiKey) {
      const newConfig = {
        provider: selectedProvider,
        model: selectedModel,
        apiKey: apiKey
      }
      setSetupData(prev => ({
        ...prev,
        llmConfigs: [...prev.llmConfigs, newConfig]
      }))
      setSelectedProvider('')
      setSelectedModel('')
      setApiKey('')
      toaster.create({
        title: 'LLM Configuration Added',
        type: 'success',
        duration: 2000
      })
    }
  }

  const removeLLMConfig = (index: number) => {
    setSetupData(prev => ({
      ...prev,
      llmConfigs: prev.llmConfigs.filter((_, i) => i !== index)
    }))
  }

  const generateEnvFile = () => {
    let envContent = '# Generated Environment Configuration\\n\\n'
    
    // Hosting configuration
    envContent += `HOSTING_TYPE=${setupData.hostingType}\\n\\n`
    
    // GitHub OAuth (only for multi-user)
    if (setupData.hostingType === 'multi-user') {
      envContent += '# GitHub OAuth Configuration\\n'
      envContent += `GITHUB_CLIENT_ID=${setupData.githubClientId}\\n`
      envContent += `GITHUB_CLIENT_SECRET=${setupData.githubClientSecret}\\n\\n`
    }
    
    // LLM Configurations
    envContent += '# LLM Provider Configurations\\n'
    setupData.llmConfigs.forEach((config, index) => {
      const providerKey = config.provider.toUpperCase()
      envContent += `${providerKey}_API_KEY=${config.apiKey}\\n`
      envContent += `${providerKey}_MODEL=${config.model}\\n`
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
    
    toaster.create({
      title: 'Environment file downloaded',
      description: 'Keep this file safe for future deployments',
      type: 'success',
      duration: 5000
    })
  }

  const handleGitHubLogin = async () => {
    // Simulate GitHub login
    setTimeout(() => {
      setIsLoggedIn(true)
      toaster.create({
        title: 'GitHub Login Successful',
        type: 'success',
        duration: 3000
      })
    }, 1000)
  }

  const toggleRepoSelection = (repoId: number, branch: string) => {
    setSetupData(prev => {
      const existingIndex = prev.selectedRepos.findIndex(r => r.repoId === repoId)
      if (existingIndex >= 0) {
        // Update branch or remove if same repo/branch
        const existing = prev.selectedRepos[existingIndex]
        if (existing.branch === branch) {
          return {
            ...prev,
            selectedRepos: prev.selectedRepos.filter(r => r.repoId !== repoId)
          }
        } else {
          return {
            ...prev,
            selectedRepos: prev.selectedRepos.map((r, i) => 
              i === existingIndex ? { ...r, branch } : r
            )
          }
        }
      } else {
        return {
          ...prev,
          selectedRepos: [...prev.selectedRepos, { repoId, branch }]
        }
      }
    })
  }

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <VStack gap={6} align="stretch">
            <Text fontSize="xl" fontWeight="bold">Hosting Configuration</Text>
            <Text fontSize="sm" opacity={0.7}>How do you want to host this application?</Text>
            <VStack gap={4}>
              <Button
                variant={setupData.hostingType === 'self' ? 'solid' : 'outline'}
                colorScheme="blue"
                size="lg"
                width="100%"
                p={8}
                onClick={() => setSetupData(prev => ({ ...prev, hostingType: 'self' }))}
              >
                <VStack gap={2}>
                  <Text fontWeight="bold">Self Use Only</Text>
                  <Text fontSize="sm" opacity={0.8}>
                    Just for personal use
                  </Text>
                </VStack>
              </Button>
              <Button
                variant={setupData.hostingType === 'multi-user' ? 'solid' : 'outline'}
                colorScheme="blue"
                size="lg"
                width="100%"
                p={8}
                onClick={() => setSetupData(prev => ({ ...prev, hostingType: 'multi-user' }))}
              >
                <VStack gap={2}>
                  <Text fontWeight="bold">Multi-User Deployment</Text>
                  <Text fontSize="sm" opacity={0.8}>
                    Allow multiple users with GitHub OAuth
                  </Text>
                </VStack>
              </Button>
            </VStack>
          </VStack>
        )

      case 2:
        if (setupData.hostingType === 'self') {
          return (
            <VStack gap={4}>
              <Box p={2} bg="blue.subtle" borderRadius="md" borderLeft="4px solid" borderColor="blue.solid">
                <Text fontWeight="normal" fontSize="sm" color="blue.fg">
                  For self-use hosting, no additional authentication setup is required.
                </Text>
              </Box>
              <Text>You can proceed to the next step.</Text>
            </VStack>
          )
        }
        return (
          <VStack gap={6} align="stretch">
            <Text fontSize="lg" fontWeight="bold">GitHub OAuth Configuration</Text>
            <Text opacity={0.7} fontSize="sm">
              To enable multi-user access, you will need to create a GitHub OAuth App and provide the credentials.
            </Text>
            <VStack gap={4} align="stretch">
              <Box>
                <Text mb={2} fontWeight="medium">GitHub Client ID</Text>
                <Input
                  placeholder="Enter your GitHub Client ID"
                  value={setupData.githubClientId}
                  onChange={(e) => setSetupData(prev => ({ ...prev, githubClientId: e.target.value }))}
                />
              </Box>
              <Box>
                <Text mb={2} fontWeight="medium">GitHub Client Secret</Text>
                <Input
                  type="password"
                  placeholder="Enter your GitHub Client Secret"
                  value={setupData.githubClientSecret}
                  onChange={(e) => setSetupData(prev => ({ ...prev, githubClientSecret: e.target.value }))}
                />
                <Text fontSize="sm" opacity={0.7} mt={1}>
                  Keep this secret safe. It will be stored in your .env file.
                </Text>
              </Box>
            </VStack>
          </VStack>
        )

      case 3:
        return (
          <VStack gap={6} align="stretch">
            <Text fontSize="lg" fontWeight="bold">LLM Provider Configuration</Text>
            <Text fontSize="sm" opacity={0.7} mb={2}>
              Setup your AI provider and model to enable intelligent features in your application.
            </Text>
            
            {/* Add new LLM configuration */}
            <Box p={4} borderWidth="1px" borderColor="border.muted" borderRadius="md" bg="bg.subtle">
              <VStack gap={4}>
                <Box width="100%">
                  <Text mb={2} fontWeight="medium">LLM Provider</Text>
                  <Combobox.Root
                    collection={createListCollection({
                      items: LLM_PROVIDERS.map(p => ({ label: p.name, value: p.id }))
                    })}
                    value={[selectedProvider]}
                    onValueChange={(e) => {
                      setSelectedProvider(e.value[0] || '')
                      setSelectedModel('')
                    }}
                    openOnClick
                  >
                    <Combobox.Control position="relative">
                      <Combobox.Input
                        placeholder="Select or search provider"
                        paddingRight="2rem"
                      />
                      <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                        <Text fontSize="sm">▼</Text>
                      </Combobox.Trigger>
                    </Combobox.Control>
                    <Combobox.Positioner>
                      <Combobox.Content>
                        {LLM_PROVIDERS.map(provider => (
                          <Combobox.Item key={provider.id} item={provider.id}>
                            <Combobox.ItemText>{provider.name}</Combobox.ItemText>
                            <Combobox.ItemIndicator />
                          </Combobox.Item>
                        ))}
                      </Combobox.Content>
                    </Combobox.Positioner>
                  </Combobox.Root>
                </Box>
                
                {selectedProvider && (
                  <Box width="100%">
                    <Text mb={2} fontWeight="medium">Model</Text>
                    <Combobox.Root
                      collection={createListCollection({
                        items: (LLM_PROVIDERS.find(p => p.id === selectedProvider)?.models || []).map(m => ({ label: m.name, value: m.id }))
                      })}
                      value={[selectedModel]}
                      onValueChange={(e) => setSelectedModel(e.value[0] || '')}
                      openOnClick
                    >
                      <Combobox.Control position="relative">
                        <Combobox.Input
                          placeholder="Select or search model"
                          paddingRight="2rem"
                        />
                        <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                          <Text fontSize="sm">▼</Text>
                        </Combobox.Trigger>
                      </Combobox.Control>
                      <Combobox.Positioner>
                        <Combobox.Content>
                          {LLM_PROVIDERS.find(p => p.id === selectedProvider)?.models.map(model => (
                            <Combobox.Item key={model.id} item={model.id}>
                              <Combobox.ItemText>{model.name}</Combobox.ItemText>
                              <Combobox.ItemIndicator />
                            </Combobox.Item>
                          ))}
                        </Combobox.Content>
                      </Combobox.Positioner>
                    </Combobox.Root>
                  </Box>
                )}
                
                {selectedModel && (
                  <Box width="100%">
                    <Text mb={2} fontWeight="medium">API Key</Text>
                    <Input
                      type="password"
                      placeholder="Enter API key"
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                    />
                  </Box>
                )}
                
                <Button
                  colorScheme="blue"
                  onClick={addLLMConfig}
                  disabled={!selectedProvider || !selectedModel || !apiKey}
                >
                  Add Configuration
                </Button>
              </VStack>
            </Box>

            {/* Display configured LLMs */}
            {setupData.llmConfigs.length > 0 && (
              <Box p={4} borderWidth="1px" borderColor="border.muted" borderRadius="md" bg="bg.subtle">
                <Text fontWeight="bold" mb={4}>Configured LLM Providers</Text>
                <VStack gap={2}>
                  {setupData.llmConfigs.map((config, index) => (
                    <HStack key={index} justify="space-between" width="100%" p={2} bg="bg.muted" borderRadius="md">
                      <Text fontSize="sm">
                        {LLM_PROVIDERS.find(p => p.id === config.provider)?.name} - {config.model}
                      </Text>
                      <Button size="sm" colorScheme="red" onClick={() => removeLLMConfig(index)}>
                        Remove
                      </Button>
                    </HStack>
                  ))}
                </VStack>
              </Box>
            )}

            {/* Download .env file */}
            {setupData.llmConfigs.length > 0 && (
              <Box p={4} borderWidth="1px" borderColor="border.muted" borderRadius="md" bg="bg.subtle">
                <VStack gap={4}>
                  <Text fontWeight="bold" fontSize="lg">Environment Configuration Ready</Text>
                  <Text fontSize="sm" textAlign="center" opacity={0.8}>
                    Download your .env file and keep it safe for future deployments.
                    This file contains your API keys and configuration.
                  </Text>
                  <Button variant="outline" onClick={downloadEnvFile}>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                        <path d="M12 16v-8m0 8l-4-4m4 4l4-4M4 20h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      Download .env File
                    </span>
                  </Button>
                </VStack>
              </Box>
            )}
          </VStack>
        )

      case 4:
        return (
          <VStack gap={6} align="stretch">
            <Text fontSize="lg" fontWeight="bold">Repository Selection</Text>
            
            {!isLoggedIn ? (
              <Box p={6} textAlign="center" borderWidth="1px" borderColor="border.muted" borderRadius="md" bg="bg.subtle">
                <VStack gap={4}>
                  <Text>Please login with GitHub to access your repositories</Text>
                  <Button colorScheme="gray" onClick={handleGitHubLogin}>
                    Login with GitHub
                  </Button>
                </VStack>
              </Box>
            ) : (
              <VStack gap={4}>
                <Box
                  p={2}
                  bg="green.subtle"
                  borderRadius="sm"
                  borderLeft="4px solid"
                  borderColor="green.solid"
                  position="fixed"
                  top="20px"
                  right="20px"
                  zIndex={1000}
                  boxShadow="md"
                >
                  <Text fontWeight="normal" fontSize="sm" color="green.600" letterSpacing="0.01em">
                    ✓ Successfully logged in to GitHub!
                  </Text>
                </Box>
                
                <Text>Select repositories and branches to clone:</Text>
                
                {/* Repository Selection */}
                <Box p={4} borderWidth="1px" borderColor="border.muted" borderRadius="md" bg="bg.subtle" width="100%">
                  <VStack gap={4}>
                    <Box width="100%">
                      <Text mb={2} fontWeight="medium">Repository</Text>
                      <Combobox.Root
                        collection={createListCollection({
                          items: SAMPLE_REPOS.map(r => ({ label: r.fullName, value: r.id.toString() }))
                        })}
                        value={[selectedRepo]}
                        onValueChange={(e) => {
                          setSelectedRepo(e.value[0] || '')
                          setSelectedBranch('')
                        }}
                        openOnClick
                      >
                        <Combobox.Control position="relative">
                          <Combobox.Input
                            placeholder="Select or search repository"
                            paddingRight="2rem"
                          />
                          <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                            <Text fontSize="sm">▼</Text>
                          </Combobox.Trigger>
                        </Combobox.Control>
                        <Combobox.Positioner>
                          <Combobox.Content>
                            {SAMPLE_REPOS.map(repo => (
                              <Combobox.Item key={repo.id} item={repo.id.toString()}>
                                <Combobox.ItemText>{repo.fullName}</Combobox.ItemText>
                                <Combobox.ItemIndicator />
                              </Combobox.Item>
                            ))}
                          </Combobox.Content>
                        </Combobox.Positioner>
                      </Combobox.Root>
                    </Box>
                    
                    {selectedRepo && (
                      <Box width="100%">
                        <Text mb={2} fontWeight="medium">Branch</Text>
                        <Combobox.Root
                          collection={createListCollection({
                            items: (SAMPLE_REPOS.find(r => r.id.toString() === selectedRepo)?.branches || []).map(b => ({ label: b, value: b }))
                          })}
                          value={[selectedBranch]}
                          onValueChange={(e) => setSelectedBranch(e.value[0] || '')}
                          openOnClick
                        >
                          <Combobox.Control position="relative">
                            <Combobox.Input
                              placeholder="Select or search branch"
                              paddingRight="2rem"
                            />
                            <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                              <Text fontSize="sm">▼</Text>
                            </Combobox.Trigger>
                          </Combobox.Control>
                          <Combobox.Positioner>
                            <Combobox.Content>
                              {SAMPLE_REPOS.find(r => r.id.toString() === selectedRepo)?.branches.map(branch => (
                                <Combobox.Item key={branch} item={branch}>
                                  <Combobox.ItemText>{branch}</Combobox.ItemText>
                                  <Combobox.ItemIndicator />
                                </Combobox.Item>
                              ))}
                            </Combobox.Content>
                          </Combobox.Positioner>
                        </Combobox.Root>
                      </Box>
                    )}
                    
                    <Button
                      colorScheme="blue"
                      onClick={() => {
                        if (selectedRepo && selectedBranch) {
                          toggleRepoSelection(parseInt(selectedRepo), selectedBranch)
                          setSelectedRepo('')
                          setSelectedBranch('')
                        }
                      }}
                      disabled={!selectedRepo || !selectedBranch}
                    >
                      Add Repository
                    </Button>
                  </VStack>
                </Box>

                {setupData.selectedRepos.length > 0 && (
                  <Box p={4} borderWidth="1px" borderColor="border.muted" borderRadius="md" bg="bg.subtle" width="100%">
                    <Text fontWeight="bold" mb={4}>Selected Repositories</Text>
                    <VStack gap={2}>
                      {setupData.selectedRepos.map((selected, index) => {
                        const repo = SAMPLE_REPOS.find(r => r.id === selected.repoId)
                        return (
                          <HStack key={index} justify="space-between" width="100%" p={2} bg="bg.muted" borderRadius="md">
                            <Text fontSize="sm">
                              {repo?.fullName} ({selected.branch})
                            </Text>
                            <Button size="sm" colorScheme="red" onClick={() => toggleRepoSelection(selected.repoId, selected.branch)}>
                              Remove
                            </Button>
                          </HStack>
                        )
                      })}
                    </VStack>
                  </Box>
                )}
              </VStack>
            )}
          </VStack>
        )

      default:
        return null
    }
  }

  return (
    <Container maxW="4xl" py={8}>
      <VStack gap={8}>
        <VStack gap={2} textAlign="center">
          <Text fontSize="3xl" fontWeight="bold" maxWidth="700px" width="100%">Setup Your Application</Text>
          <Text opacity={0.7} fontSize="sm" maxWidth="700px" width="100%">
            Follow these steps to configure your prompt repository
          </Text>
        </VStack>

        {/* Progress Steps */}
        <Box position="relative" width="100%" maxWidth="600px" mx="auto">
          <HStack gap={0} width="100%" justify="space-between" align="flex-start">
            {steps.map((step, index) => (
              <VStack key={index} flex={1} position="relative" align="center">
                <Box
                  width={10}
                  height={10}
                  borderRadius="full"
                  bg={index + 1 <= currentStep ? 'blue.solid' : 'gray.muted'}
                  color="white"
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                  fontWeight="bold"
                  zIndex={2}
                  position="relative"
                  mb={2}
                >
                  {index + 1}
                </Box>
                <Text fontSize="xs" textAlign="center" fontWeight="medium" maxWidth="160px">
                  {step.title}
                </Text>
                {/* Progress line */}
                {index < steps.length - 1 && (
                  <Box
                    position="absolute"
                    top="20px"
                    left="calc(50% + 20px)"
                    right="calc(-50% + 20px)"
                    height="2px"
                    bg={index + 1 < currentStep ? 'blue.solid' : 'gray.muted'}
                    zIndex={1}
                    transform="translateY(-50%)"
                  />
                )}
              </VStack>
            ))}
          </HStack>
        </Box>

        {/* Step Content */}
        <Box p={8} width="100%" minH="400px" borderWidth="1px" borderColor="border.muted" borderRadius="md" bg="bg.subtle">
          {renderStepContent()}
        </Box>

        {/* Navigation */}
        <HStack justify="space-between" width="100%">
          <Button
            onClick={handlePrev}
            disabled={currentStep === 1}
            variant="outline"
          >
            ← Previous
          </Button>
          
          <Text opacity={0.7} fontSize="sm">
            Step {currentStep} of {steps.length}
          </Text>
          
          {currentStep < steps.length ? (
            <Button
              onClick={handleNext}
              colorScheme="blue"
              disabled={
                (currentStep === 1 && !setupData.hostingType) ||
                (currentStep === 2 && setupData.hostingType === 'multi-user' && 
                 (!setupData.githubClientId || !setupData.githubClientSecret)) ||
                (currentStep === 3 && setupData.llmConfigs.length === 0) ||
                (currentStep === 4 && !isLoggedIn)
              }
            >
              Next →
            </Button>
          ) : (
            <Button
              colorScheme="green"
              disabled={setupData.selectedRepos.length === 0}
              onClick={() => {
                toaster.create({
                  title: 'Setup Complete!',
                  description: 'Your application is ready to use.',
                  type: 'success',
                  duration: 5000
                })
              }}
            >
              Complete Setup
            </Button>
          )}
        </HStack>
      </VStack>
    </Container>
  )
}

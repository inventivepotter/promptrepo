'use client';

import { Text, Box } from "@chakra-ui/react";
import { useEffect, useState } from "react";

const quotes = [
  {
    text: "The quality of your {**_prompts_**} determines the quality of your AI interactions. A well-crafted {**_prompt_**} is the bridge between human intention and artificial intelligence.",
    author: "AI Engineering Principles"
  },
  {
    text: "In the future, {**_prompt_**} engineering will be as essential as traditional programming. The art of communication with AI will shape the next generation of human-computer interaction.",
    author: "Future of Technology"
  },
  {
    text: "A precise {**_prompt_**} is like a compass for AI - it guides the model toward your desired destination, preventing it from wandering into irrelevant territories.",
    author: "Prompt Engineering Mastery"
  },
  {
    text: "The evolution of {**_prompts_**} mirrors the evolution of human communication - from simple commands to nuanced conversations that unlock AI's true potential.",
    author: "Digital Communication Theory"
  },
  {
    text: "Every great AI application starts with a great {**_prompt_**}. The {**_prompt_**} is not just an input; it's the architectural blueprint of your AI agent's behavior.",
    author: "AI Development Philosophy"
  },
  {
    text: "As AI becomes more sophisticated, our {**_prompts_**} must become more strategic. The future belongs to those who can speak fluently in the language of artificial minds.",
    author: "Cognitive Computing Insights"
  },
  {
    text: "The difference between a novice and an expert in AI lies not in the tools they use, but in the {**_prompts_**} they craft. Master your {**_prompts_**}, and you master the AI.",
    author: "Expert Systems Theory"
  },
  {
    text: "A single well-crafted {**_prompt_**} can unlock insights that hours of traditional programming cannot achieve. The power lies in precision, context, and intention.",
    author: "Computational Linguistics"
  },
  {
    text: "Think of {**_prompts_**} as recipes for artificial intelligence - the right ingredients, in the right order, with the right technique, yield extraordinary results.",
    author: "AI Cookbook Philosophy"
  },
  {
    text: "The art of {**_prompt_**} design is the art of constraint. By carefully limiting what we ask, we paradoxically expand what we can achieve.",
    author: "Creative AI Research"
  },
  {
    text: "In the symphony of human-AI collaboration, {**_prompts_**} are both the conductor's baton and the musical score - they guide and define the entire performance.",
    author: "Human-AI Interaction Studies"
  },
  {
    text: "The most powerful {**_prompts_**} are those that teach the AI not just what to do, but how to think about the problem. Context is king in the realm of artificial intelligence.",
    author: "Cognitive AI Architecture"
  },
  {
    text: "Every {**_prompt_**} is a hypothesis about how to communicate with an artificial mind. The best {**_prompt_**} engineers are also the best experimental scientists.",
    author: "AI Research Methodology"
  },
  {
    text: "The future of work will be defined by those who can translate human needs into AI-understandable {**_prompts_**}. This translation skill will become more valuable than traditional coding.",
    author: "Future of Work Studies"
  },
  {
    text: "A great {**_prompt_**} doesn't just give commands; it provides context, sets expectations, and creates a shared understanding between human and machine intelligence.",
    author: "Collaborative Intelligence Theory"
  },
  {
    text: "The elegance of a {**_prompt_**} lies in its ability to be simultaneously specific enough to guide and flexible enough to inspire creative AI responses.",
    author: "Prompt Design Aesthetics"
  }
];

const renderTextWithStyledPrompts = (text: string) => {
  const parts = text.split(/(\{[^}]*\})/g);
  
  return parts.map((part, index) => {
    if (part.includes('{**_prompt')) {
      // Extract the word (prompt or prompts) from the placeholder
      const word = part.includes('prompts') ? 'prompts' : 'prompt';
      return (
        <Text
          key={index}
          as="span"
          fontWeight="500"
          color="gray.500"
          borderBottom="2px solid"
          borderColor="gray.500"
          pb="2px"
          textDecorationLine="none"
          _dark={{
            color: "gray.400",
            borderColor: "gray.400"
          }}
        >
          {`{${word}}`}
        </Text>
      );
    }
    return part;
  });
};

export const PromptQuotes = () => {
  const [currentQuote, setCurrentQuote] = useState(0);

  useEffect(() => {
    // Set a random quote on mount
    setCurrentQuote(Math.floor(Math.random() * quotes.length));
  }, []);

  const quote = quotes[currentQuote];

  return (
    <Box
      p={8}
      maxW="3xl"
      mx="auto"
      textAlign="center"
    >
      <Text
        fontSize="xl"
        color="gray.700"
        lineHeight="1.7"
        mb={4}
        _dark={{
          color: "gray.300"
        }}
      >
        &ldquo;{renderTextWithStyledPrompts(quote.text)}&rdquo;
      </Text>
      <Text
        fontSize="sm"
        color="gray.500"
        fontWeight="medium"
        _dark={{
          color: "gray.400"
        }}
      >
        — {quote.author}
      </Text>
    </Box>
  );
};
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
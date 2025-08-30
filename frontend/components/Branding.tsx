"use client"

import { Text, TextProps } from "@chakra-ui/react"

interface BrandingProps extends Omit<TextProps, 'children'> {
  collapsed?: boolean
  fontSize?: TextProps['fontSize']
}

export const Branding = ({ collapsed = false, fontSize, ...props }: BrandingProps) => {
  // Default font sizes if not provided
  const defaultFontSize = collapsed ? "lg" : "xl"
  const finalFontSize = fontSize || defaultFontSize
  
  if (collapsed) {
    return (
      <Text
        fontSize={finalFontSize}
        fontWeight="300"
        letterSpacing="tight"
        {...props}
      >
        {'{'}P<Text as="span" fontWeight="700">R</Text>{'}'}
      </Text>
    )
  }

  return (
    <Text
      fontSize={finalFontSize}
      fontWeight="300"
      letterSpacing="tight"
      {...props}
    >
      {'{'}Prompt{'}'}<Text as="span" fontWeight="700"> Repo</Text>
    </Text>
  )
}

export default Branding
import Link from "next/link"
import { HStack, Text, TextProps } from "@chakra-ui/react"

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
      <Link href="/">
        <HStack gap={0}>
        <Text
          fontSize={finalFontSize}
          fontWeight="500"
          letterSpacing="tight"
          color={{ _light: "primary.400", _dark: "primary.500" }} 
          {...props}
        >
          {'{'}P
        </Text>
        <Text
          fontWeight="1000"
          fontSize={finalFontSize}
          color="fg.muted"
          >
          R
        </Text>
        <Text
          fontSize={finalFontSize}
          fontWeight="500"
          letterSpacing="tight"
          color={{ _light: "primary.400", _dark: "primary.500" }} 
          {...props}
        >
          {'}'}
        </Text>
        </HStack>
      </Link>
    )
  }

  return (
    <Link href="/">
      <HStack gap={0}>
        <Text 
          color={{ _light: "primary.400", _dark: "primary.500" }} 
          fontSize={finalFontSize}
          letterSpacing="tight"
          fontWeight="500"
          {...props}
        >
          {'{'}Prompt{'}'}
        </Text>
        <Text 
          color="fg.muted"
          fontSize={finalFontSize}
          letterSpacing="tight"
          fontWeight="1000"
          {...props}
        >
          &nbsp;Repo
        </Text>
      </HStack>
    </Link>
  )
}

export default Branding
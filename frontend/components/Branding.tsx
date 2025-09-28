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
        <Text
          fontSize={finalFontSize}
          fontWeight="300"
          letterSpacing="tight"
          {...props}
        >
          {'{'}P<Text as="span" fontWeight="700">R</Text>{'}'}
        </Text>
      </Link>
    )
  }

  return (
    <Link href="/">
      <Text
        fontSize={finalFontSize}
        letterSpacing="tight"
        {...props}
      >
        <HStack>
          <Text color={{ _light: "{colors.primary.400}", _dark: "{colors.primary.500}" }} fontWeight="500">{'{'}Prompt{'}'}</Text>
          <Text as="span" fontWeight="1000" color="fg.muted" ml="-1"> Repo</Text>
        </HStack>
      </Text>
    </Link>
  )
}

export default Branding
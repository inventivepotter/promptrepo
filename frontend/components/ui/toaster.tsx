"use client"

import {
  Toaster as ChakraToaster,
  Portal,
  Spinner,
  Stack,
  Toast,
  createToaster,
} from "@chakra-ui/react"
import { useColorModeValue } from "./color-mode"

export const toaster = createToaster({
  placement: "top-end",
  pauseOnPageIdle: true,
})

interface ToastItemProps {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  toast: any
}

const ToastItem = ({ toast }: ToastItemProps) => {
  // Call all hooks at the top level
  const successBg = useColorModeValue("primary.600", "primary.700")
  const errorBg = useColorModeValue("red.600", "red.700")
  const warningBg = useColorModeValue("orange.500", "orange.600")
  const infoBg = useColorModeValue("blue.500", "blue.600")
  const textColor = useColorModeValue("white", "white")
  const descriptionColor = useColorModeValue("gray.100", "gray.200")

  // Determine colors based on toast type
  let bg: string | undefined
  let color: string | undefined
  let descColor: string | undefined

  if (toast.type === "success") {
    bg = successBg
    color = textColor
    descColor = descriptionColor
  } else if (toast.type === "error") {
    bg = errorBg
    color = textColor
    descColor = descriptionColor
  } else if (toast.type === "warning") {
    bg = warningBg
    color = textColor
    descColor = descriptionColor
  } else if (toast.type === "info") {
    bg = infoBg
    color = textColor
    descColor = descriptionColor
  }

  return (
    <Toast.Root width={{ md: "sm" }} bg={bg} color={color}>
      {toast.type === "loading" ? (
        <Spinner size="sm" />
      ) : (
        <Toast.Indicator />
      )}
      <Stack gap="1" flex="1" maxWidth="100%">
        {toast.title && (
          <Toast.Title
            fontSize={toast.type === "success" ? "sm" : "md"}
            fontWeight="bold"
          >
            {toast.title}
          </Toast.Title>
        )}
        {toast.description && (
          <Toast.Description
            fontSize={toast.type === "success" ? "xs" : "sm"}
            fontWeight={toast.type === "success" ? "normal" : "medium"}
            color={descColor}
          >
            {toast.description}
          </Toast.Description>
        )}
      </Stack>
      {toast.action && (
        <Toast.ActionTrigger>{toast.action.label}</Toast.ActionTrigger>
      )}
      {toast.closable && <Toast.CloseTrigger />}
    </Toast.Root>
  )
}

export const Toaster = () => {
  return (
    <Portal>
      <ChakraToaster toaster={toaster} insetInline={{ mdDown: "4" }}>
        {(toast) => <ToastItem toast={toast} />}
      </ChakraToaster>
    </Portal>
  )
}

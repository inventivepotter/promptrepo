"use client"

import {
  Toaster as ChakraToaster,
  Portal,
  Spinner,
  Stack,
  Toast,
  createToaster,
} from "@chakra-ui/react"

export const toaster = createToaster({
  placement: "top-end",
  pauseOnPageIdle: true,
})

export const Toaster = () => {
  return (
    <Portal>
      <ChakraToaster toaster={toaster} insetInline={{ mdDown: "4" }}>
        {(toast) => (
          <Toast.Root width={{ md: "sm" }}>
            {toast.type === "loading" ? (
              <Spinner size="sm" color="blue.solid" />
            ) : (
              <Toast.Indicator />
            )}
            <Stack gap="1" flex="1" maxWidth="100%">
              {toast.title && (
                <Toast.Title
                  fontSize={toast.type === "success" ? "sm" : "md"}
                  fontWeight={toast.type === "success" ? "normal" : "bold"}
                  color={toast.type === "success" ? "green.600" : undefined}
                  style={toast.type === "success" ? { letterSpacing: "0.01em" } : undefined}
                >
                  {toast.title}
                </Toast.Title>
              )}
              {toast.description && (
                <Toast.Description
                  fontSize={toast.type === "success" ? "xs" : "sm"}
                  fontWeight={toast.type === "success" ? "normal" : "medium"}
                  color={toast.type === "success" ? "green.500" : undefined}
                  style={toast.type === "success" ? { letterSpacing: "0.01em" } : undefined}
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
        )}
      </ChakraToaster>
    </Portal>
  )
}

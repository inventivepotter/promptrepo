import type { Metadata } from "next"
import { Provider } from "@/components/ui/provider"
import { Toaster } from "@/components/ui/toaster"
import { GlobalLoadingOverlay } from "@/components/GlobalLoadingOverlay"
import { LayoutContent } from "@/components/LayoutContent"

export const metadata: Metadata = {
  icons: "/favicon.svg",
}

export default function RootLayout(props: { children: React.ReactNode }) {
  const { children } = props
  return (
    <html suppressHydrationWarning>
      <body>
        <Provider defaultTheme="light">
            <LayoutContent>
              {children}
            </LayoutContent>
            <Toaster />
            <GlobalLoadingOverlay />
        </Provider>
      </body>
    </html>
  )
}
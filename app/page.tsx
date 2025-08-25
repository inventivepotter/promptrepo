import Image from "next/image";
import styles from "./page.module.css";
import { Button, HStack } from "@chakra-ui/react"

const Demo = () => {
  return (
    <HStack>
      <Button>Click me</Button>
      <Button>Click me</Button>
    </HStack>
  )
}

export default function Home() {
  return (
    <Demo />
  );
}

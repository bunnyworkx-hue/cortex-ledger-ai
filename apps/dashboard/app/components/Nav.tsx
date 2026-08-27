import Image from "next/image";
import Link from "next/link";

export function Nav() {
  return (
    <nav className="border-b border-zinc-200 dark:border-zinc-800">
      <div className="mx-auto flex max-w-6xl items-center px-6 py-3">
        <Link href="/" className="flex items-center gap-2 font-semibold tracking-tight transition-colors hover:text-accent">
          <Image src="/cortex-ledger-ai-mark.png" alt="" width={42} height={28} className="rounded" priority />
          Cortex Ledger AI
        </Link>
      </div>
    </nav>
  );
}

import { create } from 'zustand'

interface Store {
  count: number
  increment: () => void
  decrement: () => void
}

export const useStore = create<Store>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 })),
})) 
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function NewKeyPage() {
  return (
    <Card className="max-w-2xl">
      <CardHeader>
        <CardTitle>Create New API Key</CardTitle>
        <CardDescription>Generate a new API key for your application</CardDescription>
      </CardHeader>
      <CardContent>
        <form className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Key Name</Label>
            <Input id="name" placeholder="Enter a name for your API key" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Input id="description" placeholder="What will this key be used for?" />
          </div>
          <Button type="submit">Generate Key</Button>
        </form>
      </CardContent>
    </Card>
  );
}
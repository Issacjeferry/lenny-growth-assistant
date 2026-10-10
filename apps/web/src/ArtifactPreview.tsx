export function ArtifactPreview({ title, html }: { title: string; html: string }) {
  return <iframe title={title} sandbox="" referrerPolicy="no-referrer" srcDoc={html}/>;
}
